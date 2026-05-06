# Especificación UI: Pantallas de Detalle de Workshop y Sesión

## 1. Resumen

Estas dos pantallas forman la experiencia central de aprendizaje para estudiantes que compraron un workshop en Arkandia Campus. La pantalla de **Detalle de Workshop** muestra todas las sesiones y recursos generales de un curso comprado. La pantalla de **Detalle de Sesión** es la interfaz principal de consumo donde los estudiantes ven las clases grabadas y acceden a materiales específicos de la sesión. Ambas pantallas están detrás de autenticación y usan español informal (tuteo) en toda la copy.

---

## 2. Estructura

### Pantalla A: Detalle de Workshop (`/products/[id]`)

```
Contenedor de Página
├── Área de Contenido Principal (columna única, centrada, max-width para legibilidad)
│   ├── Encabezado del Workshop
│   │   ├── Título (heading display)
│   │   └── Descripción (texto body, line-height cómodo)
│   │
│   ├── Sección de Sesiones (espaciado vertical grande desde el encabezado)
│   │   ├── Título de Sección ("Sesiones")
│   │   └── Lista de Sesiones (stack vertical, gap cómodo)
│   │       └── SessionCard × N (enlazado, ancho completo)
│   │
│   └── Sección de Recursos Generales (condicional, espaciado vertical grande)
│       ├── Título de Sección ("Recursos generales")
│       └── ContentList (stack vertical)
```

### Pantalla B: Detalle de Sesión (`/products/[id]/sessions/[sessionId]`)

```
Contenedor de Página
├── Área de Contenido Principal (columna única, centrada)
│   ├── Navegación
│   │   └── BackLink ("← Volver al workshop")
│   │
│   ├── Encabezado de Sesión (espaciado cómodo desde nav)
│   │   ├── Título (heading display)
│   │   └── Línea de Metadatos (label: fecha + duración)
│   │
│   ├── Sección de Video (espaciado cómodo, max-width más ancho que texto)
│   │   └── VimeoPlayer O VideoFallback
│   │
│   ├── Descripción (condicional, espaciado cómodo, max-width más estrecho)
│   │   └── Texto body
│   │
│   └── Sección de Recursos de Sesión (condicional, espaciado vertical grande)
│       ├── Título de Sección ("Recursos de la sesión")
│       └── ContentList (stack vertical)
```

**Notas de layout:**
- Ambas pantallas usan una columna única centrada.
- El contenido de texto usa un max-width más estrecho (~70 caracteres) para legibilidad.
- El reproductor de video usa un max-width más ancho (~960–1100px) para mejor visualización.
- Padding: grande en desktop, medio en móvil.

---

## 3. Componentes

### SessionCard

- **Rol:** Card de navegación que enlaza a la página de detalle de una sesión específica.
- **Anatomía:**
  - Título (texto prominente, alineado a la izquierda)
  - Línea de metadatos debajo del título: fecha formateada + duración, o texto fallback
  - Ícono chevron (alineado a la derecha, sutil)
- **Variantes:** Ninguna.
- **Estados:**
  - Default: borde sutil, fondo igual a la superficie de página
  - Hover: color del borde cambia a accent, ligera elevación de fondo
  - Focus: anillo de outline visible (color accent, con offset)
  - Active: estado presionado (ligero cambio de escala u opacidad)
- **Comportamiento:** Toda la card es clickeable. Navega al detalle de sesión. Cursor pointer.

### BackLink

- **Rol:** Elemento de navegación para volver a la pantalla anterior.
- **Anatomía:**
  - Ícono chevron apuntando a la izquierda
  - Texto del label ("Volver al workshop")
- **Variantes:** Ninguna.
- **Estados:**
  - Default: color de texto terciario/muted
  - Hover: texto cambia a color primario
  - Focus: anillo de outline visible
- **Comportamiento:** Comportamiento de link inline. No parece un botón.

### VimeoPlayer

- **Rol:** Reproductor de video embebido para grabaciones de sesiones.
- **Anatomía:**
  - Contenedor de iframe responsive con aspect ratio 16:9
  - Esquinas redondeadas (radio medio)
- **Variantes:** Ninguna.
- **Estados:**
  - Cargado: iframe de Vimeo renderiza normalmente
  - Fallback (sin URL o URL inválida): caja placeholder con mensaje centrado "Grabación no disponible aún" en color de texto secundario
- **Comportamiento:** Extrae el ID del video de Vimeo de la URL mediante patrón regex. Si la extracción falla, muestra estado fallback. El iframe permite autoplay, fullscreen, picture-in-picture.

### ContentList

- **Rol:** Muestra archivos descargables y enlaces externos asociados a un workshop o sesión.
- **Anatomía por ítem:**
  - Ícono (izquierda): indica tipo de contenido (descarga o enlace externo)
  - Bloque de texto (centro): título (prominente) + descripción opcional (secundaria, debajo)
  - Link de acción (derecha): "Descargar" para descargas, "Abrir" para enlaces
- **Variantes:** Ninguna a nivel de lista. Los ítems varían según `contentType` (download vs link).
- **Estados:**
  - Default: borde inferior sutil entre ítems
  - Hover en link de acción: subrayado o cambio de color
  - Focus en link de acción: anillo de outline visible
- **Comportamiento:** Los links de acción abren en nueva pestaña para enlaces externos. Las descargas activan el comportamiento de descarga del navegador.

### EmptyState (inline)

- **Rol:** Comunica la ausencia de contenido.
- **Anatomía:** Una sola línea de texto secundario.
- **Uso:** "Aún no hay sesiones publicadas." cuando el array de sesiones está vacío.

---

## 4. Tipografía

| Nivel | Uso | Peso | Notas |
|-------|-----|------|-------|
| Display / H1 | Título de workshop, Título de sesión | Bold | Texto más grande de la página |
| H2 | Títulos de sección ("Sesiones", "Recursos") | Semibold | Demarcación clara de secciones |
| Body | Descripción de workshop, Descripción de sesión | Regular | Line-height cómodo (1.5–1.6) |
| Label | Líneas de metadatos (fecha, duración), descripciones de ContentList | Regular | Color secundario, más pequeño que body |
| Action | Links "Descargar", "Abrir" | Medium | Color accent terciario |

Todo el texto usa la tipografía sans-serif primaria del proyecto.

---

## 5. Color

| Rol | Aplicación |
|-----|------------|
| Background (page) | Canvas principal de la página |
| Background (surface) | Cards, placeholder de video fallback |
| Foreground (primary) | Títulos, texto body, labels primarios |
| Foreground (secondary) | Metadatos, descripciones, estados vacíos, íconos chevron |
| Foreground (tertiary) | Back link, links de acción ("Descargar", "Abrir") |
| Accent (primary) | Anillos de focus, borde hover en SessionCard |
| Border (subtle) | Borde de SessionCard, separadores de ítems en ContentList (opacidad baja) |

Sin gradientes. Sin sombras decorativas. Los bordes son de 1px con opacidad reducida para sutileza.

---

## 6. Espaciado y Densidad

- **Densidad general:** Cómoda. Espacios blancos generosos para un ambiente de aprendizaje tranquilo.
- **Padding de página:** Grande (desktop), Medio (móvil).
- **Separación entre secciones:** Espaciado vertical grande entre secciones principales (encabezado → sesiones → recursos).
- **Dentro de secciones:** Gap cómodo entre ítems de lista (SessionCard, ítems de ContentList).
- **Padding interno de componentes:** Padding medio dentro de cards.
- **Targets táctiles:** Todos los elementos interactivos (cards, links) cumplen con altura mínima de 44px para touch targets.

---

## 7. Iconografía

| Ícono | Ubicación | Estilo | Tamaño |
|-------|-----------|--------|--------|
| Chevron Derecho | SessionCard, borde derecho | Outline | Igual al tamaño del texto label |
| Chevron Izquierdo | BackLink, antes del texto | Outline | Igual al tamaño del texto del link |
| Download | Ítem de ContentList (tipo download) | Outline | Ligeramente más grande que texto label |
| External Link | Ítem de ContentList (tipo link) | Outline | Ligeramente más grande que texto label |

Los íconos son de color secundario/terciario por defecto. Deben venir de un set de íconos consistente (estilo outline preferido).

---

## 8. Movimiento

- **Hover de SessionCard:** Transición rápida (~150ms) para color de borde y cambio de fondo.
- **Hover de links:** Transición rápida para cambio de color.
- **Aparición del anillo de focus:** Instantáneo o muy rápido.
- **Sin animaciones elaboradas.** Esta es una interfaz de aprendizaje enfocada en contenido.

Respetar `prefers-reduced-motion`: deshabilitar transiciones cuando el usuario prefiere movimiento reducido.

---

## 9. Responsive

| Breakpoint | Comportamiento |
|------------|----------------|
| Móvil (≤640px) | Columna única. Padding de página reducido. Cards y video a ancho completo. El max-width del texto está naturalmente limitado por la pantalla. |
| Tablet (~768px) | Columna única. Padding medio. Los contenedores de texto y video comienzan a respetar límites de max-width. |
| Desktop (≥1024px) | Columna única centrada. Padding grande. Contenedor de video más ancho que contenedor de texto. Límites claros de max-width para legibilidad. |

Ningún elemento se oculta en móvil. El layout permanece en columna única en todos los tamaños. El reproductor de video puede ser ligeramente más ancho que el contenido de texto en pantallas grandes.

---

## 10. Accesibilidad

- **Orden de tabulación:**
  1. BackLink (solo en Detalle de Sesión)
  2. SessionCards en orden del documento (Detalle de Workshop)
  3. Links de acción de ContentList en orden del documento
- **Indicadores de focus:** Todos los elementos interactivos deben tener anillos de focus visibles (color accent, offset desde el borde del elemento).
- **Requisitos ARIA:**
  - SessionCard: Puede implementarse como `<a>` con texto descriptivo; no se necesita ARIA adicional si el título es visible.
  - Elementos solo-ícono: Ninguno en este diseño (todos los íconos acompañan texto).
  - Iframe de video: Debe tener atributo `title` describiendo el contenido ("Grabación de Sesión 1").
  - Links de ContentList que abren en nueva pestaña: Considerar `aria-label` indicando comportamiento de nueva pestaña, o indicador visible.
- **Contraste:** Todo el texto debe cumplir con requisitos de contraste WCAG AA contra su fondo.
- **Lector de pantalla:** Los estados vacíos deben ser anunciados. Los títulos de sección proveen estructura.

---

## 11. Notas para el Implementador

1. **Formateo de fechas:** Usar `Intl.DateTimeFormat('es-CO', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })` para locale español de Colombia. Manejar fechas null graciosamente ("Sin fecha programada").

2. **Parsing de URL de Vimeo:** Extraer ID del video con regex `/vimeo\.com\/(\d+)/`. Si la URL es null, vacía, o no coincide, renderizar el estado fallback.

3. **Secciones condicionales:** Las secciones "Recursos generales" y "Recursos de la sesión" no deben renderizarse en absoluto (ni siquiera el título) si sus respectivos arrays están vacíos.

4. **Componentes existentes:** Asumir que el codebase tiene un componente Card base, componente Link, y librería de íconos. Reutilizar estos en lugar de crear desde cero.

5. **Errores comunes a evitar:**
   - No mostrar secciones de recursos vacías con solo un título.
   - No olvidar el anillo de focus en SessionCard (toda la card es focuseable).
   - No hardcodear formatos de fecha; usar formateo con locale.
   - No hacer el iframe de video demasiado estrecho en desktop; debe ser más ancho que la columna de texto.

6. **Idioma de la copy:** Todo el texto de UI es español informal (tuteo): "tu sesión", "Volver al workshop", "Descargar", "Abrir". Nunca usar conjugaciones formales de "usted".

---

## Cómo implementar esta spec

1. Mapear los roles de color a los tokens semánticos en el DESIGN.md del proyecto.
2. Mapear los niveles tipográficos a los definidos en la tipografía del proyecto.
3. Reutilizar componentes existentes antes de crear nuevos.
4. Verificar que cada estado descrito (hover, focus, etc.) esté implementado.
5. Verificar comportamiento responsive a 320px, 768px, 1280px.
6. Pasar el linter del proyecto y tests de regresión visual.
