---
title: Mui Navigation And Surfaces
source: mui.com/material-ui
syllabus_weeks: [11]
topics: [AppBar, Menu, Breadcrumbs, Pagination, BottomNavigation, SpeedDial, Link, Card, Paper, Accordion, Modal, Popover, Popper, Backdrop, Progress, Skeleton, Transition, ImageList, Timeline]
---



# App Bar

---
productId: material-ui
title: App Bar React component
components: AppBar, Toolbar, Menu
githubLabel: 'scope: app bar'
materialDesign: https://m2.material.io/components/app-bars-top
githubSource: packages/mui-material/src/AppBar
---

# App Bar

The App Bar displays information and actions relating to the current screen.

The top App bar provides content and actions related to the current screen. It's used for branding, screen titles, navigation, and actions.

It can transform into a contextual action bar or be used as a navbar.


## Basic App bar


## App bar with menu


## App bar with responsive menu


## App bar with search field

A side searchbar.


## Responsive App bar with Drawer


## App bar with a primary search field

A primary searchbar.


## Dense (desktop only)


## Prominent

A prominent app bar.


## Bottom App bar


## Fixed placement

When you render the app bar position fixed, the dimension of the element doesn't impact the rest of the page. This can cause some part of your content to be invisible, behind the app bar. Here are 3 possible solutions:

1. You can use `position="sticky"` instead of fixed.
2. You can render a second `<Toolbar />` component:

```jsx
function App() {
  return (
    <React.Fragment>
      <AppBar position="fixed">
        <Toolbar>{/* content */}</Toolbar>
      </AppBar>
      <Toolbar />
    </React.Fragment>
  );
}
```

3. You can use `theme.mixins.toolbar` CSS:

```jsx
const Offset = styled('div')(({ theme }) => theme.mixins.toolbar);

function App() {
  return (
    <React.Fragment>
      <AppBar position="fixed">
        <Toolbar>{/* content */}</Toolbar>
      </AppBar>
      <Offset />
    </React.Fragment>
  );
}
```

## Scrolling

You can use the `useScrollTrigger()` hook to respond to user scroll actions.

### Hide App bar

The app bar hides on scroll down to leave more space for reading.


### Elevate App bar

The app bar elevates on scroll to communicate that the user is not at the top of the page.


### Back to top

A floating action button appears on scroll to make it easy to get back to the top of the page.


### `useScrollTrigger([options]) => trigger`

#### Arguments

1. `options` (_object_ [optional]):
   - `options.disableHysteresis` (_bool_ [optional]): Defaults to `false`. Disable the hysteresis. Ignore the scroll direction when determining the `trigger` value.
   - `options.target` (_Node_ [optional]): Defaults to `window`.
   - `options.threshold` (_number_ [optional]): Defaults to `100`. Change the `trigger` value when the vertical scroll strictly crosses this threshold (exclusive).

#### Returns

`trigger`: Does the scroll position match the criteria?

#### Examples

```jsx
import useScrollTrigger from '@mui/material/useScrollTrigger';

function HideOnScroll(props) {
  const trigger = useScrollTrigger();
  return (
    <Slide in={!trigger}>
      <div>Hello</div>
    </Slide>
  );
}
```

## Enable color on dark

Following the [Material Design guidelines](https://m2.material.io/design/color/dark-theme.html), the `color` prop has no effect on the appearance of the app bar in dark mode.
You can override this behavior by setting the `enableColorOnDark` prop to `true`.



# Menus

---
productId: material-ui
title: React Menu component
components: Menu, MenuItem, MenuList, ClickAwayListener, Popover, Popper
githubLabel: 'scope: menu'
materialDesign: https://m2.material.io/components/menus
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/
githubSource: packages/mui-material/src/Menu
---

# Menu

Menus display a list of choices on temporary surfaces.

A menu displays a list of choices on a temporary surface. It appears when the user interacts with a button, or other control.


## Introduction

Menus are implemented using a collection of related components:

- Menu: The container/surface of the menu.
- Menu Item: An option for users to select from the menu.
- Menu List (optional): Alternative composable container for Menu Items—see [Composition with Menu List](#composition-with-menu-list) for details.

## Basic menu

A basic menu opens over the anchor element by default (this option can be [changed](#positioned-menu) via props). When close to a screen edge, a basic menu vertically realigns to make sure that all menu items are completely visible.

You should configure the component so that selecting an option immediately confirms it and closes the menu, as shown in the demo below.


## Icon menu

In desktop viewport, padding is increased to give more space to the menu.


## Dense menu

For the menu that has long list and long text, you can use the `dense` prop to reduce the padding and text size.


## Selected menu

If used for item selection, when opened, simple menus places the initial focus on the selected menu item.
The currently selected menu item is set using the `selected` prop (from [ListItem](/material-ui/api/list-item/)).
To use a selected menu item without impacting the initial focus, set the `variant` prop to "menu".


## Positioned menu

Because the `Menu` component uses the `Popover` component to position itself, you can use the same [positioning props](/material-ui/react-popover/#anchor-playground) to position it.
For instance, you can display the menu on top of the anchor:


## Composition with Menu List

The Menu component uses the Popover component internally.
But you might want to use a different positioning strategy, or prefer not to block scrolling, for example.

The Menu List component lets you compose your own menu for these kinds of use cases—its primary purpose is to handle focus.
See the demo below for an example of composition that uses Menu List and replaces the Menu's default Popover with a Popper component instead:


## Account menu

`Menu` content can be mixed with other components like `Avatar`.


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


The `MenuItem` is a wrapper around `ListItem` with some additional styles.
You can use the same list composition features with the `MenuItem` component:

🎨 If you are looking for inspiration, you can check [MUI Treasury's customization examples](https://mui-treasury.com/?path=/docs/menu-introduction--docs).

## Max height menu

If the height of a menu prevents all menu items from being displayed, the menu can scroll internally.


## Limitations

There is [a flexbox bug](https://issues.chromium.org/issues/40344463) that prevents `text-overflow: ellipsis` from working in a flexbox layout.
You can use the `Typography` component with `noWrap` to workaround this issue:


## Change transition

Use a different transition.


## Context menu

Here is an example of a context menu. (Right click to open.)


## Grouped Menu

Display categories with the `ListSubheader` component.


## Supplementary projects

For more advanced use cases you might be able to take advantage of:

### material-ui-popup-state

![stars](https://img.shields.io/github/stars/jcoreio/material-ui-popup-state?style=social&label=Star)
![npm downloads](https://img.shields.io/npm/dm/material-ui-popup-state.svg)

The package [`material-ui-popup-state`](https://github.com/jcoreio/material-ui-popup-state) that takes care of menu state for you in most cases.



# Breadcrumbs

---
productId: material-ui
title: React Breadcrumbs component
components: Breadcrumbs, Link, Typography
githubLabel: 'scope: breadcrumbs'
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/
githubSource: packages/mui-material/src/Breadcrumbs
---

# Breadcrumbs

A breadcrumbs is a list of links that help visualize a page's location within a site's hierarchical structure, it allows navigation up to any of the ancestors.


## Basic breadcrumbs


## Active last breadcrumb

Keep the last breadcrumb interactive.


## Custom separator

In the following examples, we are using two string separators and an SVG icon.


## Breadcrumbs with icons


## Collapsed breadcrumbs


## Condensed with menu

As an alternative, consider adding a Menu component to display the condensed links in a dropdown list:


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


## Integration with react-router


## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/)

Be sure to add a `aria-label` description on the `Breadcrumbs` component.

The accessibility of this component relies on:

- The set of links is structured using an ordered list (`<ol>` element).
- To prevent screen reader announcement of the visual separators between links, they are hidden with `aria-hidden`.
- A nav element labeled with `aria-label` identifies the structure as a breadcrumb trail and makes it a navigation landmark so that it is easy to locate.


# Pagination

---
productId: material-ui
title: React Pagination component
components: Pagination, PaginationItem, TablePagination, TablePaginationActions
githubLabel: 'scope: pagination'
githubSource: packages/mui-material/src/Pagination
---

# Pagination

The Pagination component enables the user to select a specific page from a range of pages.


## Basic pagination


## Outlined pagination


## Rounded pagination


## Pagination size


## Buttons

You can optionally enable first-page and last-page buttons, or disable the previous-page and next-page buttons.


## Custom icons

It's possible to customize the control icons.


## Pagination ranges

You can specify how many digits to display either side of current page with the `siblingCount` prop, and adjacent to the start and end page number with the `boundaryCount` prop.


## Controlled pagination


## Router integration


## `usePagination`

For advanced customization use cases, a headless `usePagination()` hook is exposed.
It accepts almost the same options as the Pagination component minus all the props
related to the rendering of JSX.
The Pagination component is built on this hook.

```jsx
import usePagination from '@mui/material/usePagination';
```


## Table pagination

The `Pagination` component was designed to paginate a list of arbitrary items when infinite loading isn't used.
It's preferred in contexts where SEO is important, for instance, a blog.

For the pagination of a large set of tabular data, you should use the `TablePagination` component.


> **Warning:**
>
> Note that the `Pagination` page prop starts at 1 to match the requirement of including the value in the URL, while the `TablePagination` page prop starts at 0 to match the requirement of zero-based JavaScript arrays that come with rendering a lot of tabular data.


You can learn more about this use case in the [table section](/material-ui/react-table/#custom-pagination-options) of the documentation.

## Accessibility

### ARIA

The root node has a role of "navigation" and aria-label "pagination navigation" by default. The page items have an aria-label that identifies the purpose of the item ("go to first page", "go to previous page", "go to page 1" etc.).
You can override these using the `getItemAriaLabel` prop.

### Keyboard

The pagination items are in tab order, with a tabindex of "0".


# Bottom Navigation

---
productId: material-ui
title: Bottom Navigation React component
components: BottomNavigation, BottomNavigationAction
githubLabel: 'scope: bottom navigation'
materialDesign: https://m2.material.io/components/bottom-navigation
githubSource: packages/mui-material/src/BottomNavigation
---

# Bottom Navigation

The Bottom Navigation bar allows movement between primary destinations in an app.

Bottom navigation bars display three to five destinations at the bottom of a screen. Each destination is represented by an icon and an optional text label. When a bottom navigation icon is tapped, the user is taken to the top-level navigation destination associated with that icon.


## Bottom navigation

When there are only **three** actions, display both icons and text labels at all times.


## Bottom navigation with no label

If there are **four** or **five** actions, display inactive views as icons only.


## Fixed positioning

This demo keeps bottom navigation fixed to the bottom, no matter the amount of content on-screen.


## Third-party routing library

One frequent use case is to perform navigation on the client only, without an HTTP round-trip to the server.
The `BottomNavigationAction` component provides the `component` prop to handle this use case.
Here is a [more detailed guide](/material-ui/integrations/routing/).


# Speed Dial

---
productId: material-ui
title: React Speed Dial component
components: SpeedDial, SpeedDialAction, SpeedDialIcon
githubLabel: 'scope: speed dial'
materialDesign: https://m2.material.io/components/buttons-floating-action-button#types-of-transitions
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/
githubSource: packages/mui-material/src/SpeedDial
---

# Speed Dial

When pressed, a floating action button can display three to six related actions in the form of a Speed Dial.

If more than six actions are needed, something other than a FAB should be used to present them.


## Basic speed dial

The floating action button can display related actions.


## Playground


## Controlled speed dial

The open state of the component can be controlled with the `open`/`onOpen`/`onClose` props.


## Custom close icon

You can provide an alternate icon for the closed and open states using the `icon` and `openIcon` props
of the `SpeedDialIcon` component.


## Persistent action tooltips

The SpeedDialActions tooltips can be displayed persistently so that users don't have to long-press to see the tooltip on touch devices.

It is enabled here across all devices for demo purposes, but in production it could use the `isTouch` logic to conditionally set the prop.


## Accessibility

### ARIA

#### Required

- You should provide an `ariaLabel` for the speed dial component.
- You should provide a tooltip title using `slotProps.tooltip.title` for each speed dial action.

#### Provided

- The Fab has `aria-haspopup`, `aria-expanded` and `aria-controls` attributes.
- The speed dial actions container has `role="menu"` and `aria-orientation` set according to the direction.
- The speed dial actions have `role="menuitem"`, and an `aria-describedby` attribute that references the associated tooltip.

### Keyboard

- The speed dial opens on focus.
- The Space and Enter keys trigger the selected speed dial action, and toggle the speed dial open state.
- The cursor keys move focus to the next or previous speed dial action. (Note that any cursor direction can be used initially to open the speed dial. This enables the expected behavior for the actual or perceived orientation of the speed dial, for example for a screen reader user who perceives the speed dial as a drop-down menu.)
- The Escape key closes the speed dial and, if a speed dial action was focused, returns focus to the Fab.


# Links

---
productId: material-ui
components: Link
githubLabel: 'scope: link'
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/link/
githubSource: packages/mui-material/src/Link
---

# Links

The Link component allows you to easily customize anchor elements with your theme colors and typography styles.


## Basic links

The Link component is built on top of the [Typography](/material-ui/api/typography/) component, meaning that you can use its props.


However, the Link component has some different default props than the Typography component:

- `color="primary"` as the link needs to stand out.
- `variant="inherit"` as the link will, most of the time, be used as a child of a Typography component.

## Underline

The `underline` prop can be used to set the underline behavior. The default is `always`.


## Security

When you use `target="_blank"` with Links, it is [recommended](https://developers.google.com/web/tools/lighthouse/audits/noopener) to always set `rel="noopener"` or `rel="noreferrer"` when linking to third party content.

- `rel="noopener"` prevents the new page from being able to access the `window.opener` property and ensures it runs in a separate process.
  Without this, the target page can potentially redirect your page to a malicious URL.
- `rel="noreferrer"` has the same effect, but also prevents the _Referer_ header from being sent to the new page.
  ⚠️ Removing the referrer header will affect analytics.

## Third-party routing library

One frequent use case is to perform navigation on the client only, without an HTTP round-trip to the server.
The `Link` component provides the `component` prop to handle this use case.
Here is a [more detailed guide](/material-ui/integrations/routing/#link).

## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/link/)

- When providing the content for the link, avoid generic descriptions like "click here" or "go to".
  Instead, use [specific descriptions](https://developers.google.com/web/tools/lighthouse/audits/descriptive-link-text).
- For the best user experience, links should stand out from the text on the page. For instance, you can keep the default `underline="always"` behavior.
- If a link doesn't have a meaningful href, [it should be rendered using a `<button>` element](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/anchor-is-valid.md).
  The demo below illustrates how to properly link with a `<button>`:


### Keyboard accessibility

- Interactive elements should receive focus in a coherent order when the user presses the <kbd class="key">Tab</kbd> key.
- Users should be able to open a link by pressing <kbd class="key">Enter</kbd>.

### Screen reader accessibility

- When a link receives focus, screen readers should announce a descriptive link name.
  If the link opens in a new window or browser tab, add an [`aria-label`](https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA8) to inform screen reader users—for example, _"To learn more, visit the About page which opens in a new window."_


# Cards

---
productId: material-ui
title: React Card component
components: Card, CardActionArea, CardActions, CardContent, CardHeader, CardMedia, Collapse, Paper
githubLabel: 'scope: card'
materialDesign: https://m2.material.io/components/cards
githubSource: packages/mui-material/src/Card
---

# Card

Cards contain content and actions about a single subject.


## Introduction

Cards are surfaces that display content and actions on a single topic.
The Material UI Card component includes several complementary utility components to handle various use cases:

- Card: a surface-level container for grouping related components.
- Card Content: the wrapper for the Card content.
- Card Header: an optional wrapper for the Card header.
- Card Media: an optional container for displaying images, videos, etc.
- Card Actions: an optional wrapper that groups a set of buttons.
- Card Action Area: an optional wrapper that allows users to interact with the specified area of the Card.


## Basics

```jsx
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
```

> **Success:**
>
> Although cards can support multiple actions, UI controls, and an overflow menu, use restraint and remember that cards are meant to be entry points to more complex and detailed information.


### Outlined Card

Set `variant="outlined"` to render an outlined card.


## Complex Interaction

On desktop, card content can expand. (Click the downward chevron to view the recipe.)


## Media

Example of a card using an image to reinforce the content.


By default, we use the combination of a `<div>` element and a _background image_ to display the media. It can be problematic in some situations, for example, you might want to display a video or a responsive image. Use the `component` prop for these use cases:


## Primary action

Often a card allow users to interact with the entirety of its surface to trigger its main action, be it an expansion, a link to another screen or some other behavior. The action area of the card can be specified by wrapping its contents in a `CardActionArea` component.


A card can also offer supplemental actions which should stand detached from the main action area in order to avoid event overlap.


## UI Controls

Supplemental actions within the card are explicitly called out using icons, text, and UI controls, typically placed at the bottom of the card.

Here's an example of a media control card.


## Active state styles

To customize a Card's styles when it's in an active state, you can attach a `data-active` attribute to the Card Action Area component and apply styles with the `&[data-active]` selector, as shown below:


🎨 If you are looking for inspiration, you can check [MUI Treasury's customization examples](https://mui-treasury.com/?path=/docs/card-introduction--docs).


# Paper

---
productId: material-ui
title: React Paper component
components: Paper
githubLabel: 'scope: paper'
materialDesign: https://m2.material.io/design/environment/elevation.html
githubSource: packages/mui-material/src/Paper
---

# Paper

The Paper component is a container for displaying content on an elevated surface.


## Introduction

In Material Design, surface components and shadow styles are heavily influenced by their real-world physical counterparts.

Material UI implements this concept with the Paper component, a container-like surface that features the [`elevation`](#elevation) prop for pulling box-shadow values from the theme.

> **Success:**
>
> The Paper component is ideally suited for designs that follow [Material Design's elevation system](https://m2.material.io/design/environment/elevation.html#elevation-in-material-design), which is meant to replicate how light casts shadows in the physical world.
> 
> If you just need a generic container, you may prefer to use the [Box](/material-ui/react-box/) or [Container](/material-ui/react-container/) components.



## Component

```jsx
import Paper from '@mui/material/Paper';
```

## Customization

### Elevation

Use the `elevation` prop to establish hierarchy through the use of shadows.
The Paper component's default elevation level is `1`.
The prop accepts values from `0` to `24`.
The higher the number, the further away the Paper appears to be from its background.

In dark mode, increasing the elevation also makes the background color lighter.
This is done by applying a semi-transparent gradient with the `background-image` CSS property.

> **Warning:**
>
> The aforementioned dark mode behavior can lead to confusion when overriding the Paper component, because changing the `background-color` property won't affect the lighter shading.
> To override it, you must either use a new background value, or customize the values for both `background-color` and `background-image`.



### Variants

Set the `variant` prop to `"outlined"` for a flat, outlined Paper with no shadows:


### Corners

The Paper component features rounded corners by default.
Add the `square` prop for square corners:


## Anatomy

The Paper component is composed of a single root `<div>` that wraps around its contents:

```html
<div class="MuiPaper-root">
  <!-- Paper contents -->
</div>
```


# Accordion

---
productId: material-ui
title: React Accordion component
components: Accordion, AccordionActions, AccordionDetails, AccordionSummary
githubLabel: 'scope: accordion'
materialDesign: https://m1.material.io/components/expansion-panels.html
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/accordion/
githubSource: packages/mui-material/src/Accordion
---

# Accordion

The Accordion component lets users show and hide sections of related content on a page.


## Introduction

The Material UI Accordion component includes several complementary utility components to handle various use cases:

- Accordion: the wrapper for grouping related components.
- Accordion Summary: the wrapper for the Accordion header, which expands or collapses the content when clicked.
- Accordion Details: the wrapper for the Accordion content.
- Accordion Actions: an optional wrapper that groups a set of buttons.


> **Info:**
>
> This component is no longer documented in the [Material Design guidelines](https://m2.material.io/), but Material UI will continue to support it.


## Basics

```jsx
import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
```

### Expand icon

Use the `expandIcon` prop on the Accordion Summary component to change the expand indicator icon.
The component handles the turning upside-down transition automatically.


### Expanded by default

Use the `defaultExpanded` prop on the Accordion component to have it opened by default.


### Transition

Use the `slots.transition` and `slotProps.transition` props to change the Accordion's default transition.


### Disabled item

Use the `disabled` prop on the Accordion component to disable interaction and focus.


### Controlled Accordion

The Accordion component can be controlled or uncontrolled.


> **Info:**
>
> - A component is **controlled** when it's managed by its parent using props.
> - A component is **uncontrolled** when it's managed by its own local state.
> 
> Learn more about controlled and uncontrolled components in the [React documentation](https://react.dev/learn/sharing-state-between-components#controlled-and-uncontrolled-components).


## Customization

### Only one expanded at a time

Use the `expanded` prop with React's `useState` hook to allow only one Accordion item to be expanded at a time.
The demo below also shows a bit of visual customization.


### Changing heading level

By default, the Accordion uses an `h3` element for the heading. You can change the heading element using the `slotProps.heading.component` prop to ensure the correct heading hierarchy in your document.

```jsx
<Accordion slotProps={{ heading: { component: 'h4' } }}>
  <AccordionSummary
    expandIcon={<ExpandMoreIcon />}
    aria-controls="panel1-content"
    id="panel1-header"
  >
    Accordion
  </AccordionSummary>
  <AccordionDetails>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse malesuada
    lacus ex, sit amet blandit leo lobortis eget.
  </AccordionDetails>
</Accordion>
```

## Performance

The Accordion content is mounted by default even if it's not expanded.
This default behavior has server-side rendering and SEO in mind.

If you render the Accordion Details with a big component tree nested inside, or if you have many Accordions, you may want to change this behavior by setting `unmountOnExit` to `true` inside the `slotProps.transition` prop to improve performance:

```jsx
<Accordion slotProps={{ transition: { unmountOnExit: true } }} />
```

## Accessibility

The [WAI-ARIA guidelines for accordions](https://www.w3.org/WAI/ARIA/apg/patterns/accordion/) recommend setting an `id` and `aria-controls`, which in this case would apply to the Accordion Summary component.
The Accordion component then derives the necessary `aria-labelledby` and `id` from its content.

```jsx
<Accordion>
  <AccordionSummary id="panel-header" aria-controls="panel-content">
    Header
  </AccordionSummary>
  <AccordionDetails>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
  </AccordionDetails>
</Accordion>
```

## Anatomy

The Accordion component consists of a root `<div>` that contains the Accordion Summary, Accordion Details, and optional Accordion Actions for action buttons.

```jsx
<div class="MuiAccordion-root">
  <h3 class="MuiAccordion-heading">
    <button class="MuiButtonBase-root MuiAccordionSummary-root" aria-expanded="">
      <!-- Accordion summary goes here -->
    </button>
  </h3>
  <div class="MuiAccordion-region" role="region">
    <div class="MuiAccordionDetails-root">
      <!-- Accordion content goes here -->
    </div>
  </div>
</div>
```


# Modal

---
productId: material-ui
title: React Modal component
components: Modal
githubLabel: 'scope: modal'
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
githubSource: packages/mui-material/src/Modal
---

# Modal

The modal component provides a solid foundation for creating dialogs, popovers, lightboxes, or whatever else.

The component renders its `children` node in front of a backdrop component.
The `Modal` offers important features:

- 💄 Manages modal stacking when one-at-a-time just isn't enough.
- 🔐 Creates a backdrop, for disabling interaction below the modal.
- 🔐 It disables scrolling of the page content while open.
- ♿️ It properly manages focus; moving to the modal content,
  and keeping it there until the modal is closed.
- ♿️ Adds the appropriate ARIA roles automatically.


> **Info:**
>
> The term "modal" is sometimes used to mean "dialog", but this is a misnomer.
> A modal window describes parts of a UI.
> An element is considered modal if [it blocks interaction with the rest of the application](https://en.wikipedia.org/wiki/Modal_window).


If you are creating a modal dialog, you probably want to use the [Dialog](/material-ui/react-dialog/) component rather than directly using Modal.
Modal is a lower-level construct that is leveraged by the following components:

- [Dialog](/material-ui/react-dialog/)
- [Drawer](/material-ui/react-drawer/)
- [Menu](/material-ui/react-menu/)
- [Popover](/material-ui/react-popover/)

## Basic modal


Notice that you can disable the outline (often blue or gold) with the `outline: 0` CSS property.

## Nested modal

Modals can be nested, for example a select within a dialog, but stacking of more than two modals, or any two modals with a backdrop is discouraged.


## Transitions

The open/close state of the modal can be animated with a transition component.
This component should respect the following conditions:

- Be a direct child descendent of the modal.
- Have an `in` prop. This corresponds to the open/close state.
- Call the `onEnter` callback prop when the enter transition starts.
- Call the `onExited` callback prop when the exit transition is completed.
  These two callbacks allow the modal to unmount the child content when closed and fully transitioned.

Modal has built-in support for [react-transition-group](https://github.com/reactjs/react-transition-group).


Alternatively, you can use [react-spring](https://github.com/pmndrs/react-spring).


## Performance

The content of modal is unmounted when closed.
If you need to make the content available to search engines or render expensive component trees inside your modal while optimizing for interaction responsiveness
it might be a good idea to change this default behavior by enabling the `keepMounted` prop:

```jsx
<Modal keepMounted />
```


As with any performance optimization, this is not a silver bullet.
Be sure to identify bottlenecks first, and then try out these optimization strategies.

## Server-side modal

React [doesn't support](https://github.com/facebook/react/issues/13097) the [`createPortal()`](https://react.dev/reference/react-dom/createPortal) API on the server.
In order to display the modal, you need to disable the portal feature with the `disablePortal` prop:


## Limitations

### Focus trap

The modal moves the focus back to the body of the component if the focus tries to escape it.

This is done for accessibility purposes. However, it might create issues.
In the event the users need to interact with another part of the page, for example with a chatbot window, you can disable the behavior:

```jsx
<Modal disableEnforceFocus />
```

## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

- Be sure to add `aria-labelledby="id..."`, referencing the modal title, to the `Modal`.
  Additionally, you may give a description of your modal with the `aria-describedby="id..."` prop on the `Modal`.

  ```jsx
  <Modal aria-labelledby="modal-title" aria-describedby="modal-description">
    <h2 id="modal-title">My Title</h2>
    <p id="modal-description">My Description
  </Modal>
  ```

- The [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/dialog/) can help you set the initial focus on the most relevant element, based on your modal content.
- Keep in mind that a "modal window" overlays on either the primary window or another modal window. Windows under a modal are **inert**. That is, users cannot interact with content outside an active modal window. This might create [conflicting behaviors](#focus-trap).


# Popover

---
productId: material-ui
title: React Popover component
components: Grow, Popover
githubLabel: 'component: Popover'
githubSource: packages/mui-material/src/Popover
---

# Popover

A Popover can be used to display some content on top of another.

Things to know when using the `Popover` component:

- The component is built on top of the [`Modal`](/material-ui/react-modal/) component.
- The scroll and click away are blocked unlike with the [`Popper`](/material-ui/react-popper/) component.


## Basic Popover


## Anchor playground

Use the radio buttons to adjust the `anchorOrigin` and `transformOrigin` positions.
You can also set the `anchorReference` to `anchorPosition` or `anchorEl`.
When it is `anchorPosition`, the component will, instead of `anchorEl`,
refer to the `anchorPosition` prop which you can adjust to set
the position of the popover.


## Mouse hover interaction

This demo demonstrates how to use the `Popover` component with `mouseenter` and `mouseleave` events to achieve popover behavior.


## Virtual element

The value of the `anchorEl` prop can be a reference to a fake DOM element.
You need to provide an object with the following interface:

```ts
interface PopoverVirtualElement {
  nodeType: 1;
  getBoundingClientRect: () => DOMRect;
}
```

Highlight part of the text to see the popover:


For more information on the virtual element's properties, see the following resources:

- [getBoundingClientRect](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect)
- [DOMRect](https://developer.mozilla.org/en-US/docs/Web/API/DOMRect)
- [Node types](https://developer.mozilla.org/en-US/docs/Web/API/Node/nodeType)

> **Warning:**
>
> The usage of a virtual element for the Popover component requires the `nodeType` property.
> This is different from virtual elements used for the [`Popper`](/material-ui/react-popper/#virtual-element) or [`Tooltip`](/material-ui/react-tooltip/#virtual-element) components, both of which don't require the property.


## Supplementary projects

For more advanced use cases, you might be able to take advantage of:

### material-ui-popup-state

![stars](https://img.shields.io/github/stars/jcoreio/material-ui-popup-state?style=social&label=Star)
![npm downloads](https://img.shields.io/npm/dm/material-ui-popup-state.svg)

The package [`material-ui-popup-state`](https://github.com/jcoreio/material-ui-popup-state) that takes care of popover state for you in most cases.



# Popper

---
productId: material-ui
title: React Popper component
components: Popper
githubLabel: 'component: Popper'
githubSource: packages/mui-material/src/Popper
---

# Popper

A Popper can be used to display some content on top of another. It's an alternative to react-popper.

Some important features of the Popper component:

- 🕷 Popper relies on the 3rd party library ([Popper.js](https://popper.js.org/docs/v2/)) for perfect positioning.
- 💄 It's an alternative API to react-popper. It aims for simplicity.
- Its child element is a [Portal](/material-ui/react-portal/) on the body of the document to avoid rendering problems.
  You can disable this behavior with `disablePortal`.
- The scroll isn't blocked like with the [Popover](/material-ui/react-popover/) component.
  The placement of the popper updates with the available area in the viewport.
- Clicking away does not hide the Popper component.
  If you need this behavior, you can use the [Click-Away Listener](/material-ui/react-click-away-listener/) - see the example in the [menu documentation section](/material-ui/react-menu/#composition-with-menu-list).
- The `anchorEl` is passed as the reference object to create a new `Popper.js` instance.


## Basic Popper


## Transitions

The open/close state of the popper can be animated with a render prop child and a transition component.
This component should respect the following conditions:

- Be a direct child descendent of the popper.
- Call the `onEnter` callback prop when the enter transition starts.
- Call the `onExited` callback prop when the exit transition is completed.
  These two callbacks allow the popper to unmount the child content when closed and fully transitioned.

Popper has built-in support for [react-transition-group](https://github.com/reactjs/react-transition-group).


Alternatively, you can use [react-spring](https://github.com/pmndrs/react-spring).


## Positioned popper


## Scroll playground


## Virtual element

The value of the `anchorEl` prop can be a reference to a fake DOM element.
You need to create an object shaped like the [`VirtualElement`](https://popper.js.org/docs/v2/virtual-elements/).

Highlight part of the text to see the popper:


## Supplementary projects

For more advanced use cases you might be able to take advantage of:

### material-ui-popup-state

![stars](https://img.shields.io/github/stars/jcoreio/material-ui-popup-state?style=social&label=Star)
![npm downloads](https://img.shields.io/npm/dm/material-ui-popup-state.svg)

The package [`material-ui-popup-state`](https://github.com/jcoreio/material-ui-popup-state) that takes care of popper state for you in most cases.



# Backdrop

---
productId: material-ui
title: Backdrop React Component
components: Backdrop
githubLabel: 'scope: backdrop'
githubSource: packages/mui-material/src/Backdrop
---

# Backdrop

The Backdrop component narrows the user's focus to a particular element on the screen.

The Backdrop signals a state change within the application and can be used for creating loaders, dialogs, and more.
In its simplest form, the Backdrop component will add a dimmed layer over your application.


## Example

The demo below shows a basic Backdrop with a Circular Progress component in the foreground to indicate a loading state.
After clicking **Show Backdrop**, you can click anywhere on the page to close it.



# Progress

---
productId: material-ui
title: Circular, Linear progress React components
components: CircularProgress, LinearProgress
githubLabel: 'scope: progress'
materialDesign: https://m2.material.io/components/progress-indicators
githubSource: packages/mui-material/src/LinearProgress
---

# Progress

Progress indicators commonly known as spinners, express an unspecified wait time or display the length of a process.

Progress indicators inform users about the status of ongoing processes, such as loading an app, submitting a form, or saving updates.

- **Determinate** indicators display how long an operation will take.
- **Indeterminate** indicators visualize an unspecified wait time.

The animations of the components rely on CSS as much as possible to work even before the JavaScript is loaded.


## Circular

### Circular indeterminate


### Circular color


### Circular size


### Circular determinate


### Circular track


### Interactive integration


### Circular with label


## Linear

### Linear indeterminate


### Linear color


### Linear determinate


### Linear buffer


### Linear with label


## Non-standard ranges

The progress components accept a value in the range 0 - 100. This simplifies things for screen-reader users, where these are the default min / max values. Sometimes, however, you might be working with a data source where the values fall outside this range. Here's how you can easily transform a value in any range to a scale of 0 - 100:

```jsx
// MIN = Minimum expected value
// MAX = Maximum expected value
// Function to normalise the values (MIN / MAX could be integrated)
const normalise = (value) => ((value - MIN) * 100) / (MAX - MIN);

// Example component that utilizes the `normalise` function at the point of render.
function Progress(props) {
  return (
    <React.Fragment>
      <CircularProgress variant="determinate" value={normalise(props.value)} />
      <LinearProgress variant="determinate" value={normalise(props.value)} />
    </React.Fragment>
  );
}
```

## Customization

Here are some examples of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


## Delaying appearance

There are [3 important limits](https://www.nngroup.com/articles/response-times-3-important-limits/) to know around response time.
The ripple effect of the `ButtonBase` component ensures that the user feels that the UI is reacting instantaneously.
Normally, no special feedback is necessary during delays of more than 0.1 but less than 1.0 second.
After 1.0 second, you can display a loader to keep user's flow of thought uninterrupted.


## Limitations

### High CPU load

Under heavy load, you might lose the stroke dash animation or see random `CircularProgress` ring widths.
You should run processor intensive operations in a web worker or by batch in order not to block the main rendering thread.

<video autoplay muted loop playsinline width="1082" height="158" style="width: 541px;">
  <source src="/static/material-ui/react-components/progress-heavy-load.mp4" type="video/mp4" />
</video>

When it's not possible, you can leverage the `disableShrink` prop to mitigate the issue.
See [this issue](https://github.com/mui/material-ui/issues/10327).


### High frequency updates

The `LinearProgress` uses a transition on the CSS transform property to provide a smooth update between different values.
The default transition duration is 200ms.
In the event a parent component updates the `value` prop too quickly, you will at least experience a 200ms delay between the re-render and the progress bar fully updated.

If you need to perform 30 re-renders per second or more, we recommend disabling the transition:

```css
.MuiLinearProgress-bar {
  transition: none;
}
```


# Skeleton

---
productId: material-ui
title: React Skeleton component
components: Skeleton
githubLabel: 'scope: skeleton'
githubSource: packages/mui-material/src/Skeleton
---

# Skeleton

Display a placeholder preview of your content before the data gets loaded to reduce load-time frustration.

The data for your components might not be immediately available. You can improve the perceived responsiveness of the page by using skeletons. It feels like things are happening immediately, then the information is incrementally displayed on the screen (Cf. [Avoid The Spinner](https://www.lukew.com/ff/entry.asp?1797)).


## Usage

The component is designed to be used **directly in your components**.
For instance:

```jsx
{
  item ? (
    <img
      style={{
        width: 210,
        height: 118,
      }}
      alt={item.title}
      src={item.src}
    />
  ) : (
    <Skeleton variant="rectangular" width={210} height={118} />
  );
}
```

## Variants

The component supports 4 shape variants:

- `text` (default): represents a single line of text (you can adjust the height via font size).
- `circular`, `rectangular`, and `rounded`: come with different border radius to let you take control of the size.


## Animations

By default, the skeleton pulsates, but you can change the animation to a wave or disable it entirely.


### Pulsate example


### Wave example


## Inferring dimensions

In addition to accepting `width` and `height` props, the component can also infer the dimensions.

It works well when it comes to typography as its height is set using `em` units.

```jsx
<Typography variant="h1">{loading ? <Skeleton /> : 'h1'}</Typography>
```


But when it comes to other components, you may not want to repeat the width and
height. In these instances, you can pass `children` and it will
infer its width and height from them.

```jsx
loading ? (
  <Skeleton variant="circular">
    <Avatar />
  </Skeleton>
) : (
  <Avatar src={data.avatar} />
);
```


## Color

The color of the component can be customized by changing its `background-color` CSS property.
This is especially useful when on a black background (as the skeleton will otherwise be invisible).


## Accessibility

Skeleton screens provide an alternative to the traditional spinner method.
Rather than showing an abstract widget, skeleton screens create anticipation of what is to come and reduce cognitive load.

The background color of the skeleton uses the least amount of luminance to be visible in good conditions (good ambient light, good screen, no visual impairments).

### ARIA

None.

### Keyboard

The skeleton is not focusable.


# Transitions

---
productId: material-ui
title: React Transition component
components: Collapse, Fade, Grow, Slide, Zoom
githubLabel: 'scope: transitions'
githubSource: packages/mui-material/src/transitions
---

# Transitions

Transitions help to make a UI expressive and easy to use.

Material UI provides transitions that can be used to introduce some basic [motion](https://m2.material.io/design/motion/) to your applications.


## Collapse

Expand from the start edge of the child element.
Use the `orientation` prop if you need a horizontal collapse.
The `collapsedSize` prop can be used to set the minimum width/height when not expanded.


## Fade

Fade in from transparent to opaque.


## Grow

Expands outwards from the center of the child element, while also fading in from transparent to opaque.

The second example demonstrates how to change the `transform-origin`, and conditionally applies
the `timeout` prop to change the entry speed.


## Slide

Slide in from the edge of the screen.
The `direction` prop controls which edge of the screen the transition starts from.

The Transition component's `mountOnEnter` prop prevents the child component from being mounted
until `in` is `true`.
This prevents the relatively positioned component from scrolling into view
from its off-screen position.
Similarly, the `unmountOnExit` prop removes the component from the DOM after it has been transition off-screen.


### Slide relative to a container

The Slide component also accepts `container` prop, which is a reference to a DOM node.
If this prop is set, the Slide component will slide from the edge of that DOM node.


## Zoom

Expand outwards from the center of the child element.

This example also demonstrates how to delay the enter transition.


## Child requirement

- **Forward the style**: To better support server rendering, Material UI provides a `style` prop to the children of some transition components (Fade, Grow, Zoom, Slide).
  The `style` prop must be applied to the DOM for the animation to work as expected.
- **Forward the ref**: The transition components require the first child element to forward its ref to the DOM node. For more details about ref, check out [Caveat with refs](/material-ui/guides/composition/#caveat-with-refs)
- **Single element**: The transition components require only one child element (`React.Fragment` is not allowed).

```jsx
// The `props` object contains a `style` prop.
// You need to provide it to the `div` element as shown here.
const MyComponent = React.forwardRef(function (props, ref) {
  return (
    <div ref={ref} {...props}>
      Fade
    </div>
  );
});

export default function Main() {
  return (
    <Fade>
      {/* MyComponent must be the only child */}
      <MyComponent />
    </Fade>
  );
}
```

## TransitionGroup

To animate a component when it is mounted or unmounted, you can use the [`TransitionGroup`](https://reactcommunity.org/react-transition-group/transition-group/) component from _react-transition-group_.
As components are added or removed, the `in` prop is toggled automatically by `TransitionGroup`.


## TransitionComponent prop

Some Material UI components use these transitions internally. These accept a `TransitionComponent` prop to customize the default transition.
You can use any of the above components or your own.
It should respect the following conditions:

- Accepts an `in` prop. This corresponds to the open/close state.
- Call the `onEnter` callback prop when the enter transition starts.
- Call the `onExited` callback prop when the exit transition is completed.
  These two callbacks allow to unmount the children when in a closed state and fully transitioned.

For more information on creating a custom transition, visit the _react-transition-group_ [`Transition` documentation](https://reactcommunity.org/react-transition-group/transition/).
You can also visit the dedicated sections of some of the components:

- [Modal](/material-ui/react-modal/#transitions)
- [Dialog](/material-ui/react-dialog/#transitions)
- [Popper](/material-ui/react-popper/#transitions)
- [Snackbar](/material-ui/react-snackbar/#transitions)
- [Tooltip](/material-ui/react-tooltip/#transitions)

## Performance & SEO

The content of transition component is mounted by default even if `in={false}`.
This default behavior has server-side rendering and SEO in mind.
If you render expensive component trees inside your transition it might be a good idea to change this default behavior by enabling the
`unmountOnExit` prop:

```jsx
<Fade in={false} unmountOnExit />
```

As with any performance optimization this is not a silver bullet.
Be sure to identify bottlenecks first and then try out these optimization strategies.


# Image List

---
productId: material-ui
title: Image List React component
components: ImageList, ImageListItem, ImageListItemBar
materialDesign: https://m2.material.io/components/image-lists
githubLabel: 'scope: image list'
githubSource: packages/mui-material/src/ImageList
---

# Image List

The Image List displays a collection of images in an organized grid.

Image lists represent a collection of items in a repeated pattern. They help improve the visual comprehension of the content they hold.


## Standard image list

Standard image lists are best for items of equal importance. They have a uniform container size, ratio, and spacing.


## Quilted image list

Quilted image lists emphasize certain items over others in a collection. They create hierarchy using varied container sizes and ratios.


## Woven image list

Woven image lists use alternating container ratios to create a rhythmic layout. A woven image list is best for browsing peer content.


## Masonry image list

Masonry image lists use dynamically sized container heights that reflect the aspect ratio of each image. This image list is best used for browsing uncropped peer content.


## Image list with title bars

This example demonstrates the use of the `ImageListItemBar` to add an overlay to each item.
The overlay can accommodate a `title`, `subtitle` and secondary action - in this example an `IconButton`.


### Title bar below image (standard)

The title bar can be placed below the image.


### Title bar below image (masonry)


## Custom image list

In this example the items have a customized titlebar, positioned at the top and with a custom gradient `titleBackground`.
The secondary action `IconButton` is positioned on the left. The `gap` prop is used to adjust the gap between items.



# Timeline

---
productId: material-ui
title: React Timeline component
components: Timeline, TimelineItem, TimelineSeparator, TimelineDot, TimelineConnector, TimelineContent, TimelineOppositeContent
githubLabel: 'scope: timeline'
packageName: '@mui/lab'
---

# Timeline

The timeline displays a list of events in chronological order.

> **Info:**
>
> This component is not documented in the [Material Design guidelines](https://m2.material.io/), but it is available in Material UI.



## Basic timeline

A basic timeline showing list of events.


## Left-positioned timeline

The main content of the timeline can be positioned on the left side relative to the time axis.


## Alternating timeline

The timeline can display the events on alternating sides.


## Reverse Alternating timeline

The timeline can display the events on alternating sides in reverse order.


## Color

The `TimelineDot` can appear in different colors from theme palette.


## Outlined


## Opposite content

The timeline can display content on opposite sides.


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


## Alignment

There are different ways in which a Timeline can be placed within the container.

You can do it by overriding the styles.

A Timeline centers itself in the container by default.

The demos below show how to adjust the relative width of the left and right sides of a Timeline:

### Left-aligned


### Right-aligned


### Left-aligned with no opposite content



# Masonry

---
productId: material-ui
title: React Masonry component
components: Masonry
githubLabel: 'scope: masonry'
---

# Masonry

Masonry lays out contents of varying dimensions as blocks of the same width and different height with configurable gaps.

Masonry maintains a list of content blocks with a consistent width but different height.
The contents are ordered by row.
If a row is already filled with the specified number of columns, the next item starts another row, and it is added to the shortest column in order to optimize the use of space.


## Basic masonry

A simple example of a `Masonry`. `Masonry` is a container for one or more items. It can receive any element including `<div />` and `<img />`.


## Image masonry

This example demonstrates the use of `Masonry` for images. `Masonry` orders its children by row.
If you'd like to order images by column, check out [ImageList](/material-ui/react-image-list/#masonry-image-list).


## Items with variable height

This example demonstrates the use of `Masonry` for items with variable height.
Items can move to other columns in order to abide by the rule that items are always added to the shortest column and hence optimize the use of space.


## Columns

This example demonstrates the use of the `columns` to configure the number of columns of a `Masonry`.


`columns` accepts responsive values:


## Spacing

This example demonstrates the use of the `spacing` to configure the spacing between items.
It is important to note that the value provided to the `spacing` prop is multiplied by the theme's spacing field.


`spacing` accepts responsive values:


## Sequential

This example demonstrates the use of the `sequential` to configure the sequential order.
With `sequential` enabled, items are added in order from left to right rather than adding to the shortest column.


## Server-side rendering

This example demonstrates the use of the `defaultHeight`, `defaultColumns` and `defaultSpacing`, which are used to
support server-side rendering.

> **Info:**
>
> `defaultHeight` should be large enough to render all rows. Also, it is worth mentioning that items are not added to the shortest column in case of server-side rendering.




# Alert

---
productId: material-ui
title: React Alert component
components: Alert, AlertTitle
githubLabel: 'scope: alert'
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/alert/
githubSource: packages/mui-material/src/Alert
---

# Alert

Alerts display brief messages for the user without interrupting their use of the app.


## Introduction

Alerts give users brief and potentially time-sensitive information in an unobtrusive manner.

The Material UI Alert component includes several props for quickly customizing its styles to provide immediate visual cues about its contents.


> **Info:**
>
> This component is no longer documented in the [Material Design guidelines](https://m2.material.io/), but Material UI will continue to support it.


### Usage

A key trait of the alert pattern is that [it should not interrupt the user's experience](https://www.w3.org/WAI/ARIA/apg/patterns/alert/) of the app.
Alerts should not be confused with alert _dialogs_ ([ARIA](https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/)), which _are_ intended to interrupt the user to obtain a response.
Use the Material UI [Dialog](/material-ui/react-dialog/) component if you need this behavior.

## Basics

```jsx
import Alert from '@mui/material/Alert';
```

The Alert component wraps around its content, and stretches to fill its enclosing container.

### Severity

The `severity` prop accepts four values representing different states—`success` (the default), `info`, `warning`, and `error`–with corresponding icon and color combinations for each:


### Variants

The Alert component comes with two alternative style options—`filled` and `outlined`—which you can set using the `variant` prop.

#### Filled


#### Outlined


> **Warning:**
>
> When using an outlined Alert with the [Snackbar](/material-ui/react-snackbar/) component, background content will be visible and bleed through the Alert by default.
> You can prevent this by adding `bgcolor: 'background.paper'` to [the `sx` prop](/material-ui/customization/how-to-customize/#the-sx-prop) on the Alert component:
> 
> ```jsx
> <Alert sx={{ bgcolor: 'background.paper' }} />
> ```
> 
> Check out the [Snackbar—customization](/material-ui/react-snackbar/#customization) doc for an example of how to use these two components together.


### Color

Use the `color` prop to override the default color for the specified [`severity`](#severity)—for instance, to apply `warning` colors to a `success` Alert:


### Actions

Add an action to your Alert with the `action` prop.
This lets you insert any element—an HTML tag, an SVG icon, or a React component such as a Material UI Button—after the Alert's message, justified to the right.

If you provide an `onClose` callback to the Alert without setting the `action` prop, the component will display a close icon (&#x2715;) by default.


### Icons

Use the `icon` prop to override an Alert's icon.
As with the [`action`](#actions) prop, your `icon` can be an HTML element, an SVG icon, or a React component.
Set this prop to `false` to remove the icon altogether.

If you need to override all instances of an icon for a given [`severity`](#severity), you can use the `iconMapping` prop instead.
You can define this prop globally by customizing your app's theme. See [Theme components—Default props](/material-ui/customization/theme-components/#theme-default-props) for details.


## Customization

### Titles

To add a title to an Alert, import the Alert Title component:

```jsx
import AlertTitle from '@mui/material/AlertTitle';
```

You can nest this component above the message in your Alert for a neatly styled and properly aligned title, as shown below:


### Transitions

You can use [Transition components](/material-ui/transitions/) like [Collapse](/material-ui/transitions/#collapse) to add motion to an Alert's entrance and exit.


## Accessibility

Here are some factors to consider to ensure that your Alert is accessible:

- Because alerts are not intended to interfere with the use of the app, your Alert component should _never_ affect the keyboard focus.
- If an alert contains an action, that action must have a `tabindex` of `0` so it can be reached by keyboard-only users.
- Essential alerts should not disappear automatically—[timed interactions](https://www.w3.org/TR/UNDERSTANDING-WCAG20/time-limits-no-exceptions.html) can make your app inaccessible to users who need extra time to understand or locate the alert.
- Alerts that occur too frequently can [inhibit the usability](https://www.w3.org/TR/UNDERSTANDING-WCAG20/time-limits-postponed.html) of your app.
- Dynamically rendered alerts are announced by screen readers; alerts that are already present on the page when it loads are _not_ announced.
- Color does not add meaning to the UI for users who require assistive technology. You must ensure that any information conveyed through color is also denoted in other ways, such as within the text of the alert itself, or with additional hidden text that's read by screen readers.

## Anatomy

The Alert component is composed of a root [Paper](/material-ui/react-paper/) component (which renders as a `<div>`) that houses an icon, a message, and an optional [action](#actions):

```html
<div class="MuiPaper-root MuiAlert-root" role="alert">
  <div class="MuiAlert-icon">
    <!-- svg icon here -->
  </div>
  <div class="MuiAlert-message">This is how an Alert renders in the DOM.</div>
  <div class="MuiAlert-action">
    <!-- optional action element here -->
  </div>
</div>
```


# Css Baseline

---
productId: material-ui
components: CssBaseline, ScopedCssBaseline
githubLabel: 'component: CssBaseline'
githubSource: packages/mui-material/src/CssBaseline
---

# CSS Baseline

The CssBaseline component helps to kickstart an elegant, consistent, and simple baseline to build upon.


## Global reset

You might be familiar with [normalize.css](https://github.com/necolas/normalize.css), a collection of HTML element and attribute style-normalizations.

```jsx
import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';

export default function MyApp() {
  return (
    <React.Fragment>
      <CssBaseline />
      {/* The rest of your application */}
    </React.Fragment>
  );
}
```

## Scoping on children

However, you might be progressively migrating a website to Material UI, using a global reset might not be an option.
It's possible to apply the baseline only to the children by using the `ScopedCssBaseline` component.

```jsx
import * as React from 'react';
import ScopedCssBaseline from '@mui/material/ScopedCssBaseline';
import MyApp from './MyApp';

export default function MyApp() {
  return (
    <ScopedCssBaseline>
      {/* The rest of your application */}
      <MyApp />
    </ScopedCssBaseline>
  );
}
```

⚠️ Make sure you import `ScopedCssBaseline` first to avoid box-sizing conflicts as in the above example.

## Approach

### Page

The `<html>` and `<body>` elements are updated to provide better page-wide defaults. More specifically:

- The margin in all browsers is removed.
- The default Material Design background color is applied.
  It's using [`theme.palette.background.default`](/material-ui/customization/default-theme/?expand-path=$.palette.background) for standard devices and a white background for print devices.
- If `enableColorScheme` is provided to `CssBaseline`, native components color will be set by applying [`color-scheme`](https://web.dev/articles/color-scheme) on `<html>`.
  The value used is provided by the theme property `theme.palette.mode`.

### Layout

- `box-sizing` is set globally on the `<html>` element to `border-box`.
  Every element—including `*::before` and `*::after` are declared to inherit this property,
  which ensures that the declared width of the element is never exceeded due to padding or border.

### Scrollbars

> **Error:**
>
> This API is deprecated.
> Consider using [color-scheme](#color-scheme) instead.


The colors of the scrollbars can be customized to improve the contrast (especially on Windows). Add this code to your theme (for dark mode).

```jsx
import darkScrollbar from '@mui/material/darkScrollbar';

const theme = createTheme({
  components: {
    MuiCssBaseline: {
      styleOverrides: (themeParam) => ({
        body: themeParam.palette.mode === 'dark' ? darkScrollbar() : null,
      }),
    },
  },
});
```

Be aware, however, that using this utility (and customizing `-webkit-scrollbar`) forces macOS to always show the scrollbar.

### Color scheme

This API is introduced in @mui/material (v5.1.0) for switching between `"light"` and `"dark"` modes of native components such as scrollbar, using the `color-scheme` CSS property.
To enable it, you can set `enableColorScheme=true` as follows:

```jsx
<CssBaseline enableColorScheme />

// or

<ScopedCssBaseline enableColorScheme >
  {/* The rest of your application using color-scheme*/}
</ScopedCssBaseline>
```

### Typography

- No base font-size is declared on the `<html>`, but 16px is assumed (the browser default).
  You can learn more about the implications of changing the `<html>` default font size in [the theme documentation](/material-ui/customization/typography/#html-font-size) page.
- Set the `theme.typography.body1` style on the `<body>` element.
- Set the font-weight to `theme.typography.fontWeightBold` for the `<b>` and `<strong>` elements.
- Custom font-smoothing is enabled for better display of the Roboto font.

## Customization

Head to the [global customization](/material-ui/customization/how-to-customize/#4-global-css-override) section of the documentation to change the output of these components.
