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
10. **UI:** la especificación visual y de interacción de las páginas de workshop y sesión vive en [`session-ui-detail-spec.md`](./session-ui-detail-spec.md). Las fases 5 y 6 implementan esa spec; las decisiones puntuales de anatomía, estados, tokens, copy y a11y se consultan ahí en lugar de duplicarse en este plan.

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

**Spec:** [`session-ui-detail-spec.md`](./session-ui-detail-spec.md) — Pantalla A (`§2.1`), componentes `SessionCard` y `EmptyState` (`§3`), tokens y densidad (`§4`–`§6`), responsive (`§9`), a11y (`§10`), notas de implementación (`§11`). Mapear roles de color y niveles tipográficos a los tokens semánticos de `frontend/DESIGN.md`; nada de valores hardcodeados.

**Cambios:**
- `frontend/src/app/products/[id]/page.tsx`: layout en columna única centrada con encabezado (título + descripción del workshop), sección "Sesiones" y sección "Recursos generales". Cada sección y su título se omiten cuando su array está vacío (sin renderizar el `<h2>` solo); en lugar de la lista de sesiones vacía, mostrar el empty state inline ("Aún no hay sesiones publicadas.").
- `frontend/src/components/SessionCard.tsx` (nuevo): `<Link href="/products/{offeringId}/sessions/{session.id}">` con título, línea de metadatos (fecha + duración o fallback "Sin fecha programada") y chevron derecho. Estados default/hover/focus/active y comportamiento de card-link según spec §3.
- Helper de fecha (en `frontend/src/lib/format.ts` o equivalente): `Intl.DateTimeFormat('es-CO', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })`, con fallback explícito para `null`. No hardcodear formatos.
- Toda la copy en español tuteo.

**Verificación:**
- [ ] `pnpm eslint src && pnpm tsc --noEmit` limpio.
- [ ] `pnpm design:check` pasa (tokens semánticos, no valores crudos).
- [ ] Manual: dashboard → workshop muestra sesiones clicables + sección de recursos generales separada al final.
- [ ] Manual: workshop sin sesiones publicadas muestra el empty state inline; workshop sin recursos generales no renderiza la sección (ni su título).
- [ ] Manual: focus ring visible al tabular sobre `<SessionCard>`; toda la card es target táctil ≥ 44px.
- [ ] Manual: a 320 / 768 / 1280 px se mantiene columna única, padding apropiado y max-width de texto cómodo (spec §9).

### Fase 6: Frontend — página de detalle de sesión

**Spec:** [`session-ui-detail-spec.md`](./session-ui-detail-spec.md) — Pantalla B (`§2.2`), componentes `BackLink`, `VimeoPlayer`, `ContentList` (`§3`), tokens y densidad (`§4`–`§6`), responsive (`§9`), a11y (`§10`), notas (`§11`). El video usa max-width más ancho que el contenedor de texto en desktop (spec §2 notas, §9).

**Cambios:**
- `frontend/src/app/products/[id]/sessions/[sessionId]/page.tsx` (nuevo): SSR con `createSupabaseServerClient`, fetch `getSession(sessionId)`. Render según spec §2.2:
  1. `<BackLink href="/products/{id}">` con label "Volver al workshop".
  2. Encabezado: título + línea de metadatos (fecha es-CO + duración).
  3. `<VimeoPlayer url={videoContent?.content_url} title={session.title} />` donde `videoContent = session.contents.find(c => c.content_type === 'video')`. Si no hay video, el componente renderiza el fallback inline; **no** se hace 404 a nivel de ruta.
  4. Descripción (condicional, solo si `session.description` existe).
  5. Sección "Recursos de la sesión" con `<ContentList items={session.contents.filter(c => c.content_type !== 'video')} />`, condicional al filtrado no vacío (sección y título omitidos cuando vacío, spec §11.3).
- `frontend/src/components/VimeoPlayer.tsx` (nuevo): regex `/vimeo\.com\/(\d+)/` para `vimeo.com/{id}` y `player.vimeo.com/video/{id}`. Iframe responsive con aspect ratio 16:9, `title="Grabación: {sessionTitle}"`, `allow="autoplay; fullscreen; picture-in-picture"`. Fallback (URL nula, vacía, o sin match): caja placeholder con texto centrado "Grabación no disponible aún" en color secundario (spec §3 VimeoPlayer).
- `frontend/src/components/BackLink.tsx` (nuevo, o reutilizar si existe): chevron izquierdo + texto, estilo de link inline (no botón). Estados según spec §3 BackLink.
- Tests vitest: `VimeoPlayer` (parseo `vimeo.com/{id}`, `player.vimeo.com/video/{id}`, fallback sin ID numérico, fallback con URL `null`/`""`).
- Toda la copy en español tuteo.

**Verificación:**
- [ ] `make check` en raíz pasa.
- [ ] `pnpm design:check` pasa.
- [ ] Manual: sesión con video → embed + descripción (si existe) + recursos. Sesión sin video → fallback inline "Grabación no disponible aún" en lugar del iframe.
- [ ] Manual: en ≥1024 px el contenedor del video es claramente más ancho que el contenedor de texto.
- [ ] Manual: orden de tabulación BackLink → links de ContentList; focus rings visibles en todos los interactivos.
- [ ] Manual: iframe expone `title` descriptivo (verificar en devtools).
- [ ] Acceso denegado: URL de sesión de workshop no comprado → 404 a nivel de ruta (devuelto por la API).

## Estrategia de testing

- **Backend unit** (fake repo): forma nueva de `OfferingDetail`; `get_session_detail` con caso sin acceso.
- **Backend HTTP**: `/catalog/{id}` payload; `/catalog/sessions/{id}` 200/404/401.
- **Frontend vitest**: `api.ts` (`getSession`), `VimeoPlayer` (parseo/fallback).
- **E2E manual**: login → dashboard → workshop → sesión → embed + recursos generales al final.
- **Performance**: `get_offering_detail` ahora hace 3 queries (offering+cohort, sessions, general_resources). Todas indexadas. Sin paginar aún.

## Preguntas abiertas

Ninguna.
