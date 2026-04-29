# ARK-24: Detalle de sesión — video, descripción y recursos

## Contexto

Estudiantes que compraron un workshop necesitan una página por sesión con video (Vimeo), descripción y recursos. En la página del workshop, las sesiones deben agruparse y los recursos sin sesión deben quedar al final como "recursos generales".

Hoy `ed_content` solo se asocia a `ed_cohort` y el detalle del workshop renderiza una lista plana. `ed_session` existe en esquema pero no se expone en la API y no tiene seed data.

## Flujo de tablas

### Workshop page `GET /catalog/{offering_id}`
```
core_offering (id = $1)
  → ed_cohort (offering_id = core_offering.id)  [ya existe en get_offering_detail]
       ├─ ed_session (cohort_id = ed_cohort.id)
       │    ORDER BY scheduled_at ASC NULLS LAST
       │    → SessionSummary[]  (id, title, scheduled_at, duration_minutes)
       │
       └─ ed_content (cohort_id = ed_cohort.id, session_id IS NULL)
            ORDER BY position
            → general_resources[]  (ContentItem)
```
Access control: ya resuelto en query 1 via `core_purchase.status='completed' AND core_client.auth_user_id=$1`.

### Session detail `GET /catalog/sessions/{session_id}`
```
ed_session (id = $1)
  JOIN ed_cohort ON ed_cohort.id = ed_session.cohort_id
  JOIN core_purchase ON core_purchase.cohort_id = ed_cohort.id
                    AND core_purchase.status = 'completed'
  JOIN core_client ON core_client.id = core_purchase.client_id
                  AND core_client.auth_user_id = $2
  → 404 si no retorna fila

ed_content (session_id = $1)
  ORDER BY position
  → SessionDetail.contents[]
```

## Estado actual

- **DB**: `ed_session(id, cohort_id, title, scheduled_at, duration_minutes, zoom_*)` — sin `description`. `ed_content(id, cohort_id, title, description, content_type, content_url, position, is_preview)` — sin `session_id`. `content_type` CHECK: `('video', 'download', 'link')`.
- **Seeds**: 5 videos + 2 downloads en `ed_content`; cero filas en `ed_session`. URLs Vimeo no tienen ID numérico (`/placeholder/sesion-N`) — inválidas para regex.
- **Backend**: `get_offering_detail` hace 2 queries; la primera ya trae `cohort_id`. `OfferingDetail.contents: list[ContentItem]` (lista plana).
- **Frontend**: `products/[id]/page.tsx` renderiza `<ContentList>` plano. Sin ruta de sesión ni componente Vimeo.
- **Auth invariant**: todo query que expone contenido filtra `core_purchase.status='completed' AND core_client.auth_user_id=<JWT sub>`.

## Decisiones

1. `ed_content.session_id` nullable FK a `ed_session(id)` → recurso de sesión; NULL → recurso general del workshop.
2. Los 2 downloads del seed son general resources (`session_id IS NULL`).
3. Video de sesión = `ed_content(content_type='video', session_id=<session>)`. Un video por sesión en seed.
4. `ed_session.title` toma los títulos actuales de `ed_content` (ej. "Sesión 1: Instrumentando el repositorio"). `ed_content.title` del video pasa a "Grabación de la Sesión".
5. Vimeo embed: regex `/vimeo\.com\/(\d+)/` — cubre `vimeo.com/{id}` y `player.vimeo.com/video/{id}`. Seeds actualizados con IDs numéricos fake (ej. `https://vimeo.com/100000001`).
6. Filtrado de video principal: en `page.tsx` de sesión — `session.contents.find(c => c.content_type === 'video')` = embed; resto → `<ContentList>`.
7. RLS: `ed_session` no tiene RLS (migration 004 solo cubre `ed_content`). Access control se hace a nivel de app en el query de detalle de sesión — suficiente mientras el backend corre con permisos de servicio.
8. API: extender `/catalog/{id}` con `sessions[]` + `general_resources[]`; agregar `GET /catalog/sessions/{session_id}`.
9. `ed_session.description` se agrega via migración.

## Fases de implementación

### Fase 1: Migración BD

**Cambios:**
- `database/migrations/006_sessions_content_link.sql` (nuevo):
  ```sql
  ALTER TABLE ed_session ADD COLUMN description text;
  ALTER TABLE ed_content ADD COLUMN session_id uuid REFERENCES ed_session(id) ON DELETE SET NULL;
  CREATE INDEX idx_ed_content_session_id ON ed_content(session_id);
  ```
- `database/seeds/seed.sql` — reescribir bloque de contenido:
  - Insertar 5 filas en `ed_session` (títulos actuales de los videos, `scheduled_at` con fechas reales, `duration_minutes=120`).
  - Insertar 5 `ed_content(content_type='video', title='Grabación de la Sesión', session_id=<session>, content_url='https://vimeo.com/10000000N')`.
  - Mantener 2 downloads con `session_id IS NULL` (general resources del workshop).
- `database/docs/data-model.md` — agregar `ed_session.description` y `ed_content.session_id` al diagrama.

**Verificación:**
- [x] `make db-init && make db-seed` sin error.
- [x] `SELECT session_id, count(*) FROM ed_content GROUP BY session_id;` — 5 filas con session_id, 2 con NULL.
- [x] `SELECT * FROM ed_session WHERE description IS NOT NULL;` — no retorna nada (description se agrega vacía en seed, se puede actualizar manualmente).

### Fase 2: Backend — modelo y `OfferingDetail`

**Objetivo:** `/catalog/{id}` retorna `sessions[]` + `general_resources[]` en vez de `contents[]`.

**Cambios:**
- `backend/app/domain/models/offering.py`:
  - Nuevo `SessionSummary(id: UUID, title: str, scheduled_at: datetime | None, duration_minutes: int | None)`.
  - `OfferingDetail`: reemplazar `contents` por `sessions: list[SessionSummary]` + `general_resources: list[ContentItem]`.
- `backend/app/domain/repositories/catalog_repo.py`: actualizar signature de `get_offering_detail`.
- `backend/app/infrastructure/persistence/pg_catalog_repo.py`:
  - Query 2: `SELECT id, title, scheduled_at, duration_minutes FROM ed_session WHERE cohort_id=$1 ORDER BY scheduled_at ASC NULLS LAST`.
  - Query 3: `SELECT ... FROM ed_content WHERE cohort_id=$1 AND session_id IS NULL ORDER BY position ASC`.
- `backend/tests/test_catalog.py`: actualizar `FakeCatalogRepo` + `SAMPLE_DETAIL`; agregar test con mezcla de sessions y general_resources.

**Verificación:**
- [x] `uv run pytest tests/test_catalog.py` pasa.
- [x] `GET /api/v1/catalog/<id>` retorna `{ sessions: [...], general_resources: [...] }` sin `contents`.

### Fase 3: Backend — endpoint de detalle de sesión

**Objetivo:** `GET /api/v1/catalog/sessions/{session_id}` con access control.

**Cambios:**
- `backend/app/domain/models/offering.py`: `SessionDetail(id, title, description, scheduled_at, duration_minutes, contents: list[ContentItem])`.
- `backend/app/domain/repositories/catalog_repo.py`: `async def get_session_detail(session_id: UUID, auth_user_id: UUID) -> SessionDetail | None`.
- `backend/app/domain/services/catalog_service.py`: `get_session_detail` delegando al repo; 404 si None.
- `backend/app/infrastructure/persistence/pg_catalog_repo.py`: query con join de access control (ver flujo arriba) + `ed_content WHERE session_id=$1 ORDER BY position`.
- `backend/app/infrastructure/routers/catalog.py`: `GET /catalog/sessions/{session_id}` — declarar ANTES de `/catalog/{offering_id}` para evitar conflicto de rutas.
- `backend/tests/test_catalog.py`: tests 200 (con contenido), 404 (sesión ajena o inexistente), 401 (sin token).

**Verificación:**
- [x] `uv run pytest -v` pasa; cobertura de 404 para sesión de workshop no comprado.
- [x] `uv run ruff check app tests && uv run pyright` limpio.

### Fase 4: Frontend — tipos y API client

**Cambios:**
- `frontend/src/types/index.ts`: agregar `SessionSummary`, `SessionDetail`; actualizar `OfferingDetail` (reemplazar `contents` por `sessions` + `generalResources`).
- `frontend/src/lib/api.ts`: actualizar `getOffering`; agregar `getSession(sessionId: string): Promise<SessionDetail>`.
- `frontend/src/lib/__tests__/api.test.ts`: tests de `getSession` (token correcto, 401, 404).

**Verificación:**
- [ ] `pnpm vitest run` pasa.
- [ ] `pnpm tsc --noEmit` limpio.

### Fase 5: Frontend — página del workshop agrupada

**Cambios:**
- `frontend/src/app/products/[id]/page.tsx`: render `sessions[]` como lista de `<SessionCard>` + sección "Recursos generales" con `<ContentList generalResources={…} />`.
- `frontend/src/components/SessionCard.tsx` (nuevo): título, fecha, duración. `<Link href="/products/{offeringId}/sessions/{session.id}">`.

**Verificación:**
- [ ] `pnpm eslint src && pnpm tsc --noEmit` limpio.
- [ ] Manual: dashboard → workshop muestra sesiones clicables + recursos generales separados.

### Fase 6: Frontend — página de detalle de sesión

**Cambios:**
- `frontend/src/app/products/[id]/sessions/[sessionId]/page.tsx` (nuevo): SSR con `createSupabaseServerClient`, fetch `getSession(sessionId)`. Render:
  1. Link de regreso a `/products/{id}`.
  2. Título + descripción (si existe).
  3. `<VimeoPlayer url={videoContent.content_url} />` donde `videoContent = session.contents.find(c => c.content_type === 'video')`.
  4. `<ContentList>` con `session.contents.filter(c => c.content_type !== 'video')`.
  5. 404 si `session.contents` no tiene ningún video — mostrar mensaje "Grabación no disponible aún".
- `frontend/src/components/VimeoPlayer.tsx` (nuevo): extrae ID con `/vimeo\.com\/(\d+)/`; embed `https://player.vimeo.com/video/{id}` en `<iframe className="w-full aspect-video" allow="autoplay; fullscreen">`. Fallback si no hay match: `<p>Video no disponible</p>`.
- Tests vitest: `VimeoPlayer` (parseo URL con `vimeo.com/{id}` y `player.vimeo.com/video/{id}`, fallback sin ID numérico).

**Verificación:**
- [ ] `make check` en raíz pasa.
- [ ] Manual: sesión con video → embed + descripción + recursos. Sesión sin video → mensaje fallback.
- [ ] Acceso denegado: URL de sesión de workshop no comprado → 404.

## Estrategia de testing

- **Backend unit** (fake repo): forma nueva de `OfferingDetail`; `get_session_detail` con caso sin acceso.
- **Backend HTTP**: `/catalog/{id}` payload; `/catalog/sessions/{id}` 200/404/401.
- **Frontend vitest**: `api.ts` (`getSession`), `VimeoPlayer` (parseo/fallback).
- **E2E manual**: login → dashboard → workshop → sesión → embed + recursos generales al final.
- **Performance**: `get_offering_detail` ahora hace 3 queries (offering+cohort, sessions, general_resources). Todas indexadas. Sin paginar aún.

## Preguntas abiertas

Ninguna.
