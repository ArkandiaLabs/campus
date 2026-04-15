# ARK-24: Detalle de sesión — video, descripción y recursos

## Contexto

Estudiantes que compraron un workshop necesitan una página por sesión con video (Vimeo), descripción y recursos. En la página del workshop, las sesiones deben agruparse y los recursos sin sesión deben quedar al final como "recursos generales".

Hoy `ed_content` solo se asocia a `ed_cohort` y el detalle del workshop renderiza una lista plana. `ed_session` existe en esquema pero no se expone en la API.

## Estado actual

- **DB**: `ed_session(id, cohort_id, title, scheduled_at, duration_minutes, zoom_*)` — sin `description`. `ed_content(id, cohort_id, title, description, content_type, content_url, position, is_preview)` — sin `session_id`.
- **Backend**: `app/domain/models/offering.py` (ContentItem, OfferingDetail), `app/domain/repositories/catalog_repo.py` (Protocol), `app/infrastructure/persistence/pg_catalog_repo.py`, `app/infrastructure/routers/catalog.py` (GET `/catalog`, GET `/catalog/{id}`).
- **Frontend**: `src/app/products/[id]/page.tsx` renderiza `OfferingDetail` con `ContentList` plano. `src/lib/api.ts` (`ApiClient.getOffering`). Sin ruta de sesión ni utilidad Vimeo.
- **Auth invariant**: todo query debe filtrar `core_purchase.status='completed' AND core_client.auth_user_id=<JWT sub>`.
- **Tests**: `tests/test_catalog.py` usa `FakeCatalogRepo`; frontend usa vitest + jsdom.

## Decisiones (respuestas del usuario)

1. `ed_content.session_id` nullable → sesión; null → recurso general.
2. Video Vimeo = `ed_content` tipo `video` ligado a sesión (no columna dedicada).
3. API: extender `/catalog/{id}` con `sessions[]` + `general_resources[]`; agregar `/catalog/sessions/{session_id}` para detalle.
4. Agregar `ed_session.description`.

## Fases de implementación

### Fase 1: Migración BD

**Objetivo**: agregar `session_id` a `ed_content` y `description` a `ed_session`.

**Cambios**:
- `database/migrations/006_sessions_content_link.sql` (nuevo):
  - `ALTER TABLE ed_session ADD COLUMN description text;`
  - `ALTER TABLE ed_content ADD COLUMN session_id uuid REFERENCES ed_session(id) ON DELETE SET NULL;`
  - `CREATE INDEX idx_ed_content_session_id ON ed_content(session_id);`
- `database/seeds/seed.sql` — agregar sesiones de ejemplo + asignar `session_id` a parte del contenido existente; dejar algún contenido con `session_id=NULL` (recurso general). Incluir al menos un `content_type='video'` con URL de Vimeo por sesión.
- `database/docs/data-model.md` — actualizar diagrama/relaciones.

**Verificación**:
- [ ] `make db-init && make db-seed` corre sin error.
- [ ] `make db-psql` → `SELECT * FROM ed_session WHERE description IS NOT NULL;` devuelve filas.
- [ ] `SELECT session_id, count(*) FROM ed_content GROUP BY session_id;` muestra mezcla de NULL y no-NULL.

### Fase 2: Backend — modelo de sesiones en detalle del workshop

**Objetivo**: `/catalog/{id}` devuelve `sessions[]` (cada una con sus recursos) + `general_resources[]`.

**Cambios**:
- `backend/app/domain/models/offering.py`:
  - Nuevo `SessionSummary(id, title, scheduled_at, duration_minutes)`.
  - `OfferingDetail`: reemplazar `contents` por `sessions: list[SessionSummary]` y `general_resources: list[ContentItem]`.
- `backend/app/domain/repositories/catalog_repo.py`: actualizar signature de `get_offering_detail` (retorna nueva forma).
- `backend/app/infrastructure/persistence/pg_catalog_repo.py`:
  - Query sesiones de la cohorte ordenadas por `scheduled_at` asc nulls last, luego `created_at`.
  - Query `ed_content` con `session_id IS NULL` para `general_resources`, ordenado por `position`.
- `backend/app/infrastructure/routers/catalog.py`: sin cambios estructurales (mismo endpoint, nuevo payload).
- `backend/tests/test_catalog.py`: actualizar `FakeCatalogRepo` y fixtures; agregar tests de nueva forma.

**Verificación**:
- [ ] `cd backend && uv run pytest -v` pasa.
- [ ] Llamada manual: `curl -H "Authorization: Bearer <jwt>" /api/v1/catalog/<id>` devuelve `sessions` + `general_resources`.

### Fase 3: Backend — endpoint de detalle de sesión

**Objetivo**: `GET /api/v1/catalog/sessions/{session_id}` devuelve sesión + recursos asociados, con chequeo de acceso.

**Cambios**:
- `backend/app/domain/models/offering.py`: `SessionDetail(id, title, description, scheduled_at, duration_minutes, contents: list[ContentItem])`.
- `backend/app/domain/repositories/catalog_repo.py`: `async def get_session_detail(session_id: UUID, auth_user_id: UUID) -> SessionDetail | None`.
- `backend/app/domain/services/catalog_service.py`: método `get_session_detail` delegando al repo; 404 si None.
- `backend/app/infrastructure/persistence/pg_catalog_repo.py`:
  - Query: join `ed_session → ed_cohort → core_purchase → core_client` con invariante de acceso (`purchase.status='completed' AND client.auth_user_id=$2`). Luego `ed_content WHERE session_id=$1 ORDER BY position`.
- `backend/app/infrastructure/routers/catalog.py`: `GET /catalog/sessions/{session_id}` → 200/404. **Importante**: agregar ruta ANTES de `/catalog/{offering_id}` si hubiera conflicto, o usar `/sessions/{id}` anidado distinto. Revisar orden de declaración.
- `backend/tests/test_catalog.py`: tests de servicio (fake repo) + HTTP (200, 404 para sesión ajena, 401 sin token).

**Verificación**:
- [ ] `uv run pytest -v` pasa, cobertura de 404 para sesión de workshop no comprado.
- [ ] `uv run ruff check app tests && uv run pyright` limpio.

### Fase 4: Frontend — tipos y API client

**Objetivo**: tipos compartidos + métodos `getOffering` (payload nuevo) y `getSession(sessionId)`.

**Cambios**:
- `frontend/src/types/index.ts`: `SessionSummary`, `SessionDetail`; actualizar `OfferingDetail`.
- `frontend/src/lib/api.ts`: actualizar `getOffering`; agregar `getSession(sessionId)`.
- `frontend/src/lib/__tests__/api.test.ts`: tests de `getSession` (token, 401, 404).

**Verificación**:
- [ ] `pnpm vitest run` pasa.
- [ ] `pnpm tsc --noEmit` limpio.

### Fase 5: Frontend — página del workshop agrupada por sesiones

**Objetivo**: `/products/[id]` muestra bloque por sesión (link al detalle) + sección "Recursos generales".

**Cambios**:
- `frontend/src/app/products/[id]/page.tsx`: render `sessions[]` como cards/links a `/products/[id]/sessions/[sessionId]`; al final renderizar `general_resources` usando `ContentList` existente.
- `frontend/src/components/SessionCard.tsx` (nuevo): card con título, `scheduled_at`, duración. Link `<Link href="/products/{offeringId}/sessions/{id}">`.

**Verificación**:
- [ ] `pnpm eslint src && pnpm tsc --noEmit` limpio.
- [ ] Navegación manual: dashboard → workshop muestra sesiones + recursos generales separados.

### Fase 6: Frontend — página de detalle de sesión

**Objetivo**: `/products/[id]/sessions/[sessionId]` con video Vimeo embebido, descripción y lista de recursos.

**Cambios**:
- `frontend/src/app/products/[id]/sessions/[sessionId]/page.tsx` (nuevo): SSR con `createSupabaseServerClient`, fetch `getSession`. Render: título, descripción (si existe), video Vimeo (primer `content_type='video'`), resto de contenidos con `ContentList`.
- `frontend/src/components/VimeoPlayer.tsx` (nuevo): iframe responsive (16:9). Extrae ID de Vimeo de URL (regex `vimeo.com/(\d+)`); embed `https://player.vimeo.com/video/{id}`. Fallback: link directo.
- `frontend/src/components/ContentList.tsx`: sin cambios (ya maneja download/link/video); filtrar el video principal antes de pasar al listado para no duplicar.
- Tests vitest para `VimeoPlayer` (parseo de URL) y SSR de la página.

**Verificación**:
- [ ] `make check` en raíz pasa.
- [ ] Manual: entrar a sesión → se ve video embebido + descripción + recursos. Recurso link abre en nueva pestaña.
- [ ] Acceso denegado: intentar sesión de workshop no comprado → 404.

## Estrategia de testing

- **Backend unit** (fake repo): formato nuevo de `OfferingDetail`, `get_session_detail` incluyendo caso de acceso no autorizado (retorna None).
- **Backend HTTP**: `/catalog/{id}` payload; `/catalog/sessions/{id}` 200/404/401.
- **Frontend vitest**: `api.ts` (`getSession`), `VimeoPlayer` (parseo/fallback).
- **E2E manual**: login → dashboard → workshop → sesión; verificar recursos generales separados; verificar recursos sin sesión al final.
- **Performance**: `/catalog/{id}` ahora hace 3 queries (offering, sessions, general_resources). Aceptable; todas indexadas. No paginar aún.

## Preguntas abiertas

- Orden sesiones: `scheduled_at` asc, ¿NULLS primero o último? (asumido: last)
- ¿Mostrar sesiones futuras sin grabación? (asumido: sí; sin video, mostrar descripción + Zoom si aplica — fuera de alcance ARK-24)
- ¿Qué hacer si hay >1 video en una sesión? (asumido: primero = principal, resto en lista)
- Formato Vimeo URL en seeds: ¿`vimeo.com/{id}` o `player.vimeo.com/video/{id}`? Regex debe cubrir ambos.
