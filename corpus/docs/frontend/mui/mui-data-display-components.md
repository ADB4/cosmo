---
title: Mui Data Display Components
source: mui.com/material-ui
syllabus_weeks: [11]
topics: [Table, sorting, pagination, dense table, Tabs, vertical tabs, scrollable, Typography, Avatar, Badge, Chip, Tooltip, Icon, List]
---



# Table

---
productId: material-ui
title: React Table component
components: Table, TableBody, TableCell, TableContainer, TableFooter, TableHead, TablePagination, TableRow, TableSortLabel
githubLabel: 'scope: table'
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/table/
materialDesign: https://m2.material.io/components/data-tables
githubSource: packages/mui-material/src/Table
---

# Table

Tables display sets of data. They can be fully customized.

Tables display information in a way that's easy to scan, so that users can look for patterns and insights. They can be embedded in primary content, such as cards. They can include:

- A corresponding visualization
- Navigation
- Tools to query and manipulate data


## Introduction

Tables are implemented using a collection of related components:

- `<TableContainer />`: A wrapper that provides horizontally scrolling behavior for the `<Table />` component.
- `<Table />`: The main component for the table element. Renders as a `<table>` by default.
- `<TableHead />`: The container for the header row(s) of `<Table />`. Renders as a `<thead>` by default.
- `<TableBody />`: The container for the body rows of `<Table />`. Renders as a `<tbody>` by default.
- `<TableRow />`: A row in a table. Can be used in `<TableHead />`, `<TableBody />`, or `<TableFooter />`. Renders as a `<tr>` by default.
- `<TableCell />`: A cell in a table. Can be used in `<TableRow />` . Renders as a `<th>` in `<TableHead />` and `<td>` in `<TableBody />` by default.
- `<TableFooter />`: An optional container for the footer row(s) of the table. Renders as a `<tfoot>` by default.
- `<TablePagination />`: A component that provides controls for paginating table data. See the ['Sorting & selecting' example](#sorting-selecting) and ['Custom Table Pagination Action' example](#custom-pagination-actions).
- `<TableSortLabel />`: A component used to display sorting controls for column headers, allowing users to sort data in ascending or descending order. See the ['Sorting & selecting' example](#sorting-selecting).

## Basic table

A simple example with no frills.


## Data table

The `Table` component has a close mapping to the native `<table>` elements.
This constraint makes building rich data tables challenging.

The [`DataGrid` component](/x/react-data-grid/) is designed for use-cases that are focused on handling large amounts of tabular data.
While it comes with a more rigid structure, in exchange, you gain more powerful features.


## Dense table

A simple example of a dense table with no frills.


## Sorting & selecting

This example demonstrates the use of `Checkbox` and clickable rows for selection, with a custom `Toolbar`. It uses the `TableSortLabel` component to help style column headings.

The Table has been given a fixed width to demonstrate horizontal scrolling. In order to prevent the pagination controls from scrolling, the TablePagination component is used outside of the Table. (The ['Custom Table Pagination Action' example](#custom-pagination-actions) below shows the pagination within the TableFooter.)


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


### Custom pagination options

It's possible to customize the options shown in the "Rows per page" select using the `rowsPerPageOptions` prop.
You should either provide an array of:

- **numbers**, each number will be used for the option's label and value.

  ```jsx
  <TablePagination rowsPerPageOptions={[10, 50]} />
  ```

- **objects**, the `value` and `label` keys will be used respectively for the value and label of the option (useful for language strings such as 'All').

  ```jsx
  <TablePagination rowsPerPageOptions={[10, 50, { value: -1, label: 'All' }]} />
  ```

### Custom pagination actions

The `ActionsComponent` prop of the `TablePagination` component allows the implementation of custom actions.


## Sticky header

Here is an example of a table with scrollable rows and fixed column headers.
It leverages the `stickyHeader` prop.


## Column grouping

You can group column headers by rendering multiple table rows inside a table head:

```jsx
<TableHead>
  <TableRow />
  <TableRow />
</TableHead>
```


## Collapsible table

An example of a table with expandable rows, revealing more information.
It utilizes the [`Collapse`](/material-ui/api/collapse/) component.


## Spanning table

A simple example with spanning rows & columns.


## Virtualized table

In the following example, we demonstrate how to use [react-virtuoso](https://github.com/petyosi/react-virtuoso) with the `Table` component.
It renders 200 rows and can easily handle more.
Virtualization helps with performance issues.


## Accessibility

(WAI tutorial: <https://www.w3.org/WAI/tutorials/tables/>)

### Caption

A caption functions like a heading for a table. Most screen readers announce the content of captions. Captions help users to find a table and understand what it's about and decide if they want to read it.



# Tabs

---
productId: material-ui
title: React Tabs component
components: Tabs, Tab, TabScrollButton, TabContext, TabList, TabPanel
githubLabel: 'scope: tabs'
materialDesign: https://m2.material.io/components/tabs
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/tabs/
githubSource: packages/mui-material/src/Tabs
---

# Tabs

Tabs make it easy to explore and switch between different views.

Tabs organize and allow navigation between groups of content that are related and at the same level of hierarchy.


## Introduction

Tabs are implemented using a collection of related components:

- `<Tab />` - the tab element itself. Clicking on a tab displays its corresponding panel.
- `<Tabs />` - the container that houses the tabs. Responsible for handling focus and keyboard navigation between tabs.


## Basics

```jsx
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
```

## Experimental API

`@mui/lab` offers utility components that inject props to implement accessible tabs
following [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/):

- `<TabList />` - the container that houses the tabs. Responsible for handling focus and keyboard navigation between tabs.
- `<TabPanel />` - the card that hosts the content associated with a tab.
- `<TabContext />` - the top-level component that wraps the Tab List and Tab Panel components.


## Wrapped labels

Long labels will automatically wrap on tabs.
If the label is too long for the tab, it will overflow, and the text will not be visible.


## Colored tab


## Disabled tab

A tab can be disabled by setting the `disabled` prop.


## Fixed tabs

Fixed tabs should be used with a limited number of tabs, and when a consistent placement will aid muscle memory.

### Full width

The `variant="fullWidth"` prop should be used for smaller views.


### Centered

The `centered` prop should be used for larger views.


## Scrollable tabs

### Automatic scroll buttons

Use the `variant="scrollable"` and `scrollButtons="auto"` props to display left and right scroll buttons on desktop that are hidden on mobile:


### Forced scroll buttons

Apply `scrollButtons={true}` and the `allowScrollButtonsMobile` prop to display the left and right scroll buttons on all viewports:


If you want to make sure the buttons are always visible, you should customize the opacity.

```css
.MuiTabs-scrollButtons.Mui-disabled {
  opacity: 0.3;
}
```


### Prevent scroll buttons

Left and right scroll buttons are never be presented with `scrollButtons={false}`.
All scrolling must be initiated through user agent scrolling mechanisms (for example left/right swipe, shift mouse wheel, etc.)


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


🎨 If you are looking for inspiration, you can check [MUI Treasury's customization examples](https://mui-treasury.com/?path=/docs/tabs-introduction--docs).

## Vertical tabs

To make vertical tabs instead of default horizontal ones, there is `orientation="vertical"`:


Note that you can restore the scrollbar with `visibleScrollbar`.

## Nav tabs

By default, tabs use a `button` element, but you can provide your custom tag or component. Here's an example of implementing tabbed navigation:


### Third-party routing library

One frequent use case is to perform navigation on the client only, without an HTTP round-trip to the server.
The `Tab` component provides the `component` prop to handle this use case.
Here is a [more detailed guide](/material-ui/integrations/routing/#tabs).

## Icon tabs

Tab labels may be either all icons or all text.



## Icon position

By default, the icon is positioned at the `top` of a tab. Other supported positions are `start`, `end`, `bottom`.


## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)

The following steps are needed in order to provide necessary information for assistive technologies:

1. Label `Tabs` via `aria-label` or `aria-labelledby`.
2. `Tab`s need to be connected to their
   corresponding `[role="tabpanel"]` by setting the correct `id`, `aria-controls` and `aria-labelledby`.

An example for the current implementation can be found in the demos on this page. We've also published [an experimental API](#experimental-api) in `@mui/lab` that does not require
extra work.

### Keyboard navigation

The components implement keyboard navigation using the "manual activation" behavior.
If you want to switch to the "selection automatically follows focus" behavior you have to pass `selectionFollowsFocus` to the `Tabs` component.
The WAI-ARIA authoring practices have a detailed guide on [how to decide when to make selection automatically follow focus](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/#x6-4-deciding-when-to-make-selection-automatically-follow-focus).

#### Demo

The following two demos only differ in their keyboard navigation behavior.
Focus a tab and navigate with arrow keys to notice the difference, for example <kbd class="key">Arrow Left</kbd>.

```jsx
/* Tabs where selection follows focus */
<Tabs selectionFollowsFocus />
```


```jsx
/* Tabs where each tab needs to be selected manually */
<Tabs />
```



# Typography

---
productId: material-ui
title: React Typography component
components: Typography
githubLabel: 'scope: typography'
materialDesign: https://m2.material.io/design/typography/the-type-system.html
githubSource: packages/mui-material/src/Typography
---

# Typography

Use typography to present your design and content as clearly and efficiently as possible.


## Roboto font

Material UI uses the [Roboto](https://fonts.google.com/specimen/Roboto) font by default.
Add it to your project via Fontsource, or with the Google Fonts CDN.

<codeblock storageKey="package-manager">

```bash npm
npm install @fontsource/roboto
```

```bash pnpm
pnpm add @fontsource/roboto
```

```bash yarn
yarn add @fontsource/roboto
```

</codeblock>

Then you can import it in your entry point like this:

```tsx
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
```

> **Info:**
>
> Fontsource can be configured to load specific subsets, weights, and styles. Material UI's default typography configuration relies only on the 300, 400, 500, and 700 font weights.


### Google Web Fonts

To install Roboto through the Google Web Fonts CDN, add the following code inside your project's `<head />` tag:

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
/>
```

## Component

### Usage

The Typography component follows the [Material Design typographic scale](https://m2.material.io/design/typography/#type-scale) that provides a limited set of type sizes that work well together for a consistent layout.


### Theme keys

In some situations you might not be able to use the Typography component.
Hopefully, you might be able to take advantage of the [`typography`](/material-ui/customization/default-theme/?expand-path=$.typography) keys of the theme.


## Customization

### Adding & disabling variants

In addition to using the default typography variants, you can add custom ones, or disable any you don't need. See the [Adding & disabling variants](/material-ui/customization/typography/#adding-disabling-variants) page for more info.

### Changing the semantic element

The Typography component uses the `variantMapping` prop to associate a UI variant with a semantic element.
It's important to realize that the style of a typography component is independent from the semantic underlying element.

To change the underlying element for a one-off situation, like avoiding two `h1` elements in your page, use the `component` prop:

```jsx
<Typography variant="h1" component="h2">
  h1. Heading
</Typography>
```

To change the typography element mapping globally, [use the theme](/material-ui/customization/typography/#adding-disabling-variants):

```js
const theme = createTheme({
  components: {
    MuiTypography: {
      defaultProps: {
        variantMapping: {
          h1: 'h2',
          h2: 'h2',
          h3: 'h2',
          h4: 'h2',
          h5: 'h2',
          h6: 'h2',
          subtitle1: 'h2',
          subtitle2: 'h2',
          body1: 'span',
          body2: 'span',
        },
      },
    },
  },
});
```

### System props

> **Info:**
>
> System props are deprecated and will be removed in the next major release. Please use the `sx` prop instead.
> 
> ```diff
> - <Typography mt={2} />
> + <Typography sx={{ mt: 2 }} />
> ```


## Accessibility

Key factors to follow for an accessible typography:

- **Color**. Provide enough contrast between text and its background, check out the minimum recommended [WCAG 2.0 color contrast ratio](https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast-contrast.html) (4.5:1).
- **Font size**. Use [relative units (rem)](/material-ui/customization/typography/#font-size), instead of pixels, to accommodate the user's browser settings.
- **Heading hierarchy**. Based on [the W3 guidelines](https://www.w3.org/WAI/tutorials/page-structure/headings/), don't skip heading levels. Make sure to [separate the semantics from the style](#changing-the-semantic-element).


# Avatars

---
productId: material-ui
title: React Avatar component
components: Avatar, AvatarGroup, Badge
githubLabel: 'scope: avatar'
githubSource: packages/mui-material/src/Avatar
---

# Avatar

Avatars are found throughout material design with uses in everything from tables to dialog menus.


## Image avatars

Image avatars can be created by passing standard `img` props `src` or `srcSet` to the component.


## Letter avatars

Avatars containing simple characters can be created by passing a string as `children`.


You can use different background colors for the avatar.
The following demo generates the color based on the name of the person.


## Sizes

You can change the size of the avatar with the `height` and `width` CSS properties.


## Icon avatars

Icon avatars are created by passing an icon as `children`.


## Variants

If you need square or rounded avatars, use the `variant` prop.


## Fallbacks

If there is an error loading the avatar image, the component falls back to an alternative in the following order:

- the provided children
- the first letter of the `alt` text
- a generic avatar icon


## Grouped

`AvatarGroup` renders its children as a stack. Use the `max` prop to limit the number of avatars.


### Total avatars

If you need to control the total number of avatars not shown, you can use the `total` prop.


### Custom surplus

Set the `renderSurplus` prop as a callback to customize the surplus avatar. The callback will receive the surplus number as an argument based on the children and the `max` prop, and should return a `React.ReactNode`.

The `renderSurplus` prop is useful when you need to render the surplus based on the data sent from the server.


### Spacing

You can change the spacing between avatars using the `spacing` prop. You can use one of the presets (`"medium"`, the default, or `"small"`) or set a custom numeric value.


## With badge


## Avatar upload



# Badges

---
productId: material-ui
title: React Badge component
components: Badge
githubLabel: 'scope: badge'
githubSource: packages/mui-material/src/Badge
---

# Badge

Badge generates a small badge to the top-right of its child(ren).


## Basic badge

Examples of badges containing text, using primary and secondary colors. The badge is applied to its children.


## Color

Use `color` prop to apply theme palette to component.


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


## Badge visibility

The visibility of badges can be controlled using the `invisible` prop.


The badge hides automatically when `badgeContent` is zero. You can override this with the `showZero` prop.


## Maximum value

You can use the `max` prop to cap the value of the badge content.


## Dot badge

The `dot` prop changes a badge into a small dot. This can be used as a notification that something has changed without giving a count.


## Badge overlap

You can use the `overlap` prop to place the badge relative to the corner of the wrapped element.


## Badge alignment

You can use the `anchorOrigin` prop to move the badge to any corner of the wrapped element.


## Accessibility

You can't rely on the content of the badge to be announced correctly.
You should provide a full description, for instance, with `aria-label`:



# Chips

---
productId: material-ui
title: React Chip component
components: Chip
githubLabel: 'scope: chip'
materialDesign: https://m2.material.io/components/chips
githubSource: packages/mui-material/src/Chip
---

# Chip

Chips are compact elements that represent an input, attribute, or action.

Chips allow users to enter information, make selections, filter content, or trigger actions.

While included here as a standalone component, the most common use will
be in some form of input, so some of the behavior demonstrated here is
not shown in context.


## Basic chip

The `Chip` component supports outlined and filled styling.


## Chip actions

You can use the following actions.

- Chips with the `onClick` prop defined change appearance on focus, hover, and click.
- Chips with the `onDelete` prop defined will display a delete icon which changes appearance on hover.

### Clickable


### Deletable


### Clickable and deletable


### Clickable link


### Custom delete icon


## Chip adornments

You can add ornaments to the beginning of the component.

Use the `avatar` prop to add an avatar or use the `icon` prop to add an icon.

### Avatar chip


### Icon chip


## Color chip

You can use the `color` prop to define a color from theme palette.


## Sizes chip

You can use the `size` prop to define a small Chip.


## Multiline chip

By default, Chips displays labels only in a single line.
To have them support multiline content, use the `sx` prop to add `height:auto` to the Chip component, and `whiteSpace: normal` to the `label` styles.


## Chip array

An example of rendering multiple chips from an array of values.
Deleting a chip removes it from the array. Note that since no
`onClick` prop is defined, the `Chip` can be focused, but does not
gain depth while clicked or touched.


## Chip playground


## Accessibility

If the Chip is deletable or clickable then it is a button in tab order. When the Chip is focused (for example when tabbing) releasing (`keyup` event) `Backspace` or `Delete` will call the `onDelete` handler while releasing `Escape` will blur the Chip.


# Tooltips

---
productId: material-ui
title: React Tooltip component
components: Tooltip
githubLabel: 'scope: tooltip'
materialDesign: https://m2.material.io/components/tooltips
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/
githubSource: packages/mui-material/src/Tooltip
---

# Tooltip

Tooltips display informative text when users hover over, focus on, or tap an element.

When activated, Tooltips display a text label identifying an element, such as a description of its function.


## Basic tooltip


## Labels and descriptions

By default, the tooltip only labels its child element.
This is notably different from `title` which can either label or describe its child depending on whether the child already has a label.
For example, in the element below, the `title` acts as an accessible description:

```html
<button title="some more information">A button</button>
```

If you want the tooltip to act as an accessible description, you can pass the `describeChild` prop.
You shouldn't use `describeChild` if the tooltip provides the only visual label.
In that case, the child would have no accessible name and the tooltip would violate [success criterion 2.5.3 in WCAG 2.1](https://www.w3.org/WAI/WCAG21/Understanding/label-in-name.html).
If the trigger already has either visible text or an `aria-label`, use the tooltip as a description and pass the `describeChild` prop.
Otherwise, you can use the default behavior and let the tooltip label the trigger.


## Positioned tooltips

The `Tooltip` has 12 **placement** choices.
They don't have directional arrows; instead, they rely on motion emanating from the source to convey direction.


## Customization

Here are some examples of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


## Arrow tooltips

You can use the `arrow` prop to give your tooltip an arrow indicating which element it refers to.


## Distance from anchor

To adjust the distance between the tooltip and its anchor, you can use the `slotProps` prop to modify the [offset](https://popper.js.org/docs/v2/modifiers/offset/) of the popper.


Alternatively, you can use the `slotProps` prop to customize the margin of the popper.


## Custom child element

The tooltip needs to apply DOM event listeners to its child element.
If the child is a custom React element, you need to make sure that it spreads its props to the underlying DOM element.

```jsx
const MyComponent = React.forwardRef(function MyComponent(props, ref) {
  //  Spread the props to the underlying DOM element.
  return (
    <div {...props} ref={ref}>
      Bin
    </div>
  );
});

// ...

<Tooltip title="Delete">
  <MyComponent />
</Tooltip>;
```

If using a class component as a child, you'll also need to ensure that the ref is forwarded to the underlying DOM element. (A ref to the class component itself will not work.)

```jsx
class MyComponent extends React.Component {
  render() {
    const { innerRef, ...props } = this.props;
    //  Spread the props to the underlying DOM element.
    return (
      <div {...props} ref={innerRef}>
        Bin
      </div>
    );
  }
}

// Wrap MyComponent to forward the ref as expected by Tooltip
const WrappedMyComponent = React.forwardRef(function WrappedMyComponent(props, ref) {
  return <MyComponent {...props} innerRef={ref} />;
});

// ...

<Tooltip title="Delete">
  <WrappedMyComponent />
</Tooltip>;
```

## Triggers

You can define the types of events that cause a tooltip to show.

The touch action requires a long press due to the `enterTouchDelay` prop being set to `700`ms by default.


## Controlled tooltips

You can use the `open`, `onOpen` and `onClose` props to control the behavior of the tooltip.


## Variable width

The `Tooltip` wraps long text by default to make it readable.


## Interactive

Tooltips are interactive by default (to pass [WCAG 2.1 success criterion 1.4.13](https://www.w3.org/TR/WCAG21/#content-on-hover-or-focus)).
It won't close when the user hovers over the tooltip before the `leaveDelay` is expired.
You can disable this behavior (thus failing the success criterion which is required to reach level AA) by passing `disableInteractive`.


## Disabled elements

By default disabled elements like `<button>` do not trigger user interactions so a `Tooltip` will not activate on normal events like hover. To accommodate disabled elements, add a simple wrapper element, such as a `span`.

> **Warning:**
>
> In order to work with Safari, you need at least one display block or flex item below the tooltip wrapper.



> **Warning:**
>
> If you're not wrapping a Material UI component that inherits from `ButtonBase`, for instance, a native `<button>` element, you should also add the CSS property _pointer-events: none;_ to your element when disabled:


```jsx
<Tooltip describeChild title="You don't have permission to do this">
  <span>
    <button disabled={disabled} style={disabled ? { pointerEvents: 'none' } : {}}>
      A disabled button
    </button>
  </span>
</Tooltip>
```

## Transitions

Use a different transition.


## Follow cursor

You can enable the tooltip to follow the cursor by setting `followCursor={true}`.


## Virtual element

In the event you need to implement a custom placement, you can use the `anchorEl` prop:
The value of the `anchorEl` prop can be a reference to a fake DOM element.
You need to create an object shaped like the [`VirtualElement`](https://popper.js.org/docs/v2/virtual-elements/).


## Showing and hiding

The tooltip is normally shown immediately when the user's mouse hovers over the element, and hides immediately when the user's mouse leaves. A delay in showing or hiding the tooltip can be added through the `enterDelay` and `leaveDelay` props.

On mobile, the tooltip is displayed when the user longpresses the element and hides after a delay of 1500ms. You can disable this feature with the `disableTouchListener` prop.


## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/)

Tooltips should wrap triggers that are focusable and hoverable (for example, buttons) so that all users can activate them. When tooltips are displayed, they are automatically linked to the trigger. The trigger element is either labeled or described by the tooltip content. However, tooltip content should not be used as a full text alternative for truncated content.


# Icons

---
productId: material-ui
title: React Icon Component
components: Icon, SvgIcon
githubLabel: 'components: SvgIcon'
materialDesign: https://m2.material.io/design/iconography/system-icons.html
---

# Icons

Guidance and suggestions for using icons with Material UI.

Material UI provides icon support in three ways:

1. With [Material Icons](#material-svg-icons) exported as React components (SVG icons).
1. With the [SvgIcon](#svgicon) component, a React wrapper for custom SVG icons.
1. With the [Icon](#icon-font-icons) component, a React wrapper for custom font icons.

## Material SVG icons

Google has created over 2,100 official [Material icons](https://fonts.google.com/icons?icon.set=Material+Icons), each in five different "themes" (see below).
For each SVG icon, we export the respective React component from the `@mui/icons-material` package.
You can [search the full list of these icons](/material-ui/material-icons/).

### Installation

Run one of the following commands to install it and save it to your `package.json` dependencies:

<!-- #npm-tag-reference -->

<codeblock storageKey="package-manager">
```bash npm
npm install @mui/icons-material@next
```

```bash pnpm
pnpm add @mui/icons-material@next
```

```bash yarn
yarn add @mui/icons-material@next
```

</codeblock>

These components use the Material UI `SvgIcon` component to render the SVG path for each icon, and so have a peer-dependency on `@mui/material`.

If you aren't already using Material UI in your project, you can add it following the [installation guide](/material-ui/getting-started/installation/).

### Usage

Import icons using one of these two options:

- Option 1:

  ```jsx
  import AccessAlarmIcon from '@mui/icons-material/AccessAlarm';
  import ThreeDRotation from '@mui/icons-material/ThreeDRotation';
  ```

- Option 2:

  ```jsx
  import { AccessAlarm, ThreeDRotation } from '@mui/icons-material';
  ```

The safest for bundle size is Option 1, but some developers prefer Option 2.
Make sure you read the [minimizing bundle size guide](/material-ui/guides/minimizing-bundle-size/) before using the second approach.

Each Material icon also has a "theme": Filled (default), Outlined, Rounded, Two-tone, and Sharp. To import the icon component with a theme other than the default, append the theme name to the icon name. For example `@mui/icons-material/Delete` icon with:

- Filled theme (default) is exported as `@mui/icons-material/Delete`,
- Outlined theme is exported as `@mui/icons-material/DeleteOutlined`,
- Rounded theme is exported as `@mui/icons-material/DeleteRounded`,
- Twotone theme is exported as `@mui/icons-material/DeleteTwoTone`,
- Sharp theme is exported as `@mui/icons-material/DeleteSharp`.

> **Warning:**
>
> The Material Design guidelines name the icons using "snake_case" naming (for example `delete_forever`, `add_a_photo`), while `@mui/icons-material` exports the respective icons using "PascalCase" naming (for example `DeleteForever`, `AddAPhoto`). There are three exceptions to this naming rule: `3d_rotation` exported as `ThreeDRotation`, `4k` exported as `FourK`, and `360` exported as `ThreeSixty`.



## SvgIcon

If you need a custom SVG icon (not available in the [Material Icons](/material-ui/material-icons/)) you can use the `SvgIcon` wrapper.
This component extends the native `<svg>` element:

- It comes with built-in accessibility.
- SVG elements should be scaled for a 24x24px viewport so that the resulting icon can be used as is, or included as a child for other Material UI components that use icons.
  This can be customized with the `viewBox` attribute.
  To inherit the `viewBox` value from the original image, the `inheritViewBox` prop can be used.
- By default, the component inherits the current color. Optionally, you can apply one of the theme colors using the `color` prop.
- It supports `<svg>` element as a child so you can copy and paste your SVG directly to `SvgIcon` component.


### Color


### Size


### Component prop

You can use the `SvgIcon` wrapper even if your icons are saved in the `.svg` format.
[svgr](https://github.com/gregberge/svgr) has loaders to import SVG files and use them as React components. For example, with webpack:

```jsx
// webpack.config.js
{
  test: /\.svg$/,
  use: ['@svgr/webpack'],
}

// ---
import StarIcon from './star.svg';

<SvgIcon component={StarIcon} inheritViewBox />
```

It's also possible to use it with "url-loader" or "file-loader". This is the approach used by Create React App.

```jsx
// webpack.config.js
{
  test: /\.svg$/,
  use: ['@svgr/webpack', 'url-loader'],
}

// ---
import { ReactComponent as StarIcon } from './star.svg';

<SvgIcon component={StarIcon} inheritViewBox />
```

### createSvgIcon

The `createSvgIcon` utility component is used to create the [Material Icons](#material-svg-icons). It can be used to wrap an `<svg>` element or an SVG path which is passed as a child to the [`SvgIcon`](#svgicon) component.

```jsx
const HomeIcon = createSvgIcon(
  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />,
  'Home',
);

// or with custom SVG
const PlusIcon = createSvgIcon(
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className="h-6 w-6"
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
  </svg>,
  'Plus',
);
```


### Font Awesome

If you find that there are layout issues when using FontAwesomeIcon from `@fortawesome/react-fontawesome`, you can try passing the Font Awesome SVG data directly to SvgIcon.

Below is a comparison of the `FontAwesomeIcon` component and a wrapped `SvgIcon` component.


FontAwesomeIcon's `fullWidth` prop can also be used to approximate the correct dimensions, but it isn't perfect.

### Other libraries

#### MDI

[materialdesignicons.com](https://pictogrammers.com/library/mdi/) provides over 2,000 icons.
For the wanted icon, copy the SVG `path` they provide, and use it as the child of the `SvgIcon` component, or with `createSvgIcon()`.

Note: [mdi-material-ui](https://github.com/TeamWertarbyte/mdi-material-ui) has already wrapped each of these SVG icons with the `SvgIcon` component, so you don't have to do it yourself.

## Icon (Font icons)

The `Icon` component will display an icon from any icon font that supports ligatures.
As a prerequisite, you must include one, such as the
[Material Icons font](https://google.github.io/material-design-icons/#icon-font-for-the-web) in your project.
To use an icon simply wrap the icon name (font ligature) with the `Icon` component,
for example:

```jsx
import Icon from '@mui/material/Icon';

<Icon>star</Icon>;
```

By default, an Icon will inherit the current text color.
Optionally, you can set the icon color using one of the theme color properties: `primary`, `secondary`, `action`, `error` & `disabled`.

### Font Material Icons

`Icon` will by default set the correct base class name for the Material Icons font (filled variant).
All you need to do is load the font, for instance, via Google Web Fonts:

```html
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/icon?family=Material+Icons"
/>
```


### Custom font

For other fonts, you can customize the baseline class name using the `baseClassName` prop.
For instance, you can display two-tone icons with Material Design:

```jsx
import Icon from '@mui/material/Icon';

<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/css?family=Material+Icons+Two+Tone"
  // Import the two tones MD variant                           ^^^^^^^^
/>;
```


#### Global base class name

Modifying the `baseClassName` prop for each component usage is repetitive.
You can change the default prop globally with the theme

```js
const theme = createTheme({
  components: {
    MuiIcon: {
      defaultProps: {
        // Replace the `material-icons` default value.
        baseClassName: 'material-icons-two-tone',
      },
    },
  },
});
```

Then, you can use the two-tone font directly:

```jsx
<Icon>add_circle</Icon>
```

### Font Awesome

[Font Awesome](https://fontawesome.com/icons) can be used with the `Icon` component as follows:


Note that the Font Awesome icons weren't designed like the Material Icons (compare the two previous demos).
The fa icons are cropped to use all the space available. You can adjust for this with a global override:

```js
const theme = createTheme({
  components: {
    MuiIcon: {
      styleOverrides: {
        root: {
          // Match 24px = 3 * 2 + 1.125 * 16
          boxSizing: 'content-box',
          padding: 3,
          fontSize: '1.125rem',
        },
      },
    },
  },
});
```


## Font vs. SVGs: Which approach to use?

Both approaches work fine, however, there are some subtle differences, especially in terms of performance and rendering quality.
Whenever possible SVG is preferred as it allows code splitting, supports more icons, and renders faster and better.

For more details, take a look at [why GitHub migrated from font icons to SVG icons](https://github.blog/engineering/delivering-octicons-with-svg/).

## Accessibility

Icons can convey all sorts of meaningful information, so it's important to ensure they are accessible where appropriate.
There are two use cases you'll want to consider:

- **Decorative icons** that are only being used for visual or branding reinforcement.
  If they were removed from the page, users would still understand and be able to use your page.
- **Semantic icons** are ones that you're using to convey meaning, rather than just pure decoration.
  This includes icons without text next to them that are used as interactive controls — buttons, form elements, toggles, etc.

### Decorative icons

If your icons are purely decorative, you're already done!
The `aria-hidden=true` attribute is added so that your icons are properly accessible (invisible).

### Semantic icons

#### Semantic SVG icons

You should include the `titleAccess` prop with a meaningful value.
The `role="img"` attribute and the `<title>` element are added so that your icons are correctly accessible.

In the case of focusable interactive elements, for example when used with an icon button, you can use the `aria-label` prop:

```jsx
import IconButton from '@mui/material/IconButton';
import SvgIcon from '@mui/material/SvgIcon';

// ...

<IconButton aria-label="delete">
  <SvgIcon>
    <path d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z" />
  </SvgIcon>
</IconButton>;
```

#### Semantic font icons

You need to provide a text alternative that is only visible to assistive technologies.

```jsx
import Box from '@mui/material/Box';
import Icon from '@mui/material/Icon';
import { visuallyHidden } from '@mui/utils';

// ...

<Icon>add_circle</Icon>
<Box component="span" sx={visuallyHidden}>Create a user</Box>
```

#### Reference

- https://www.tpgi.com/using-aria-enhance-svg-accessibility/


# Lists

---
productId: material-ui
title: React List component
components: Collapse, Divider, List, ListItem, ListItemButton, ListItemAvatar, ListItemIcon, ListItemSecondaryAction, ListItemText, ListSubheader
githubLabel: 'scope: list'
materialDesign: https://m2.material.io/components/lists
githubSource: packages/mui-material/src/List
---

# Lists

Lists are continuous, vertical indexes of text or images.

Lists are a continuous group of text or images. They are composed of items containing primary and supplemental actions, which are represented by icons and text.


## Introduction

Lists present information in a concise, easy-to-follow format through a continuous, vertical index of text or images.

Material UI Lists are implemented using a collection of related components:

- List: a wrapper for list items. Renders as a `<ul>` by default.
- List Item: a common list item. Renders as an `<li>` by default.
- List Item Button: an action element to be used inside a list item.
- List Item Icon: an icon to be used inside of a list item.
- List Item Avatar: an avatar to be used inside of a list item.
- List Item Text: a container inside a list item, used to display text content.
- List Divider: a separator between list items.
- List Subheader: a label for a nested list.


The last item of the previous demo shows how you can render a link:

```jsx
<ListItemButton component="a" href="#simple-list">
  <ListItemText primary="Spam" />
</ListItemButton>
```

You can find a [demo with React Router following this section](/material-ui/integrations/routing/#list) of the documentation.

## Basics

```jsx
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
```

## Nested List


## Folder List


## Interactive

Below is an interactive demo that lets you explore the visual results of the different settings:


## Selected ListItem


## Align list items

When displaying three lines or more, the avatar is not aligned at the top.
You should set the `alignItems="flex-start"` prop to align the avatar at the top, following the Material Design guidelines:


## List Controls

### Checkbox

A checkbox can either be a primary action or a secondary action.

The checkbox is the primary action and the state indicator for the list item. The comment button is a secondary action and a separate target.


The checkbox is the secondary action for the list item and a separate target.


### Switch

The switch is the secondary action and a separate target.


## Sticky subheader

Upon scrolling, subheaders remain pinned to the top of the screen until pushed off screen by the next subheader.
This feature relies on CSS sticky positioning.


## Inset List Item

The `inset` prop enables a list item that does not have a leading icon or avatar to align correctly with items that do.


## Gutterless list

When rendering a list within a component that defines its own gutters, `ListItem` gutters can be disabled with `disableGutters`.


## Virtualized List

In the following example, we demonstrate how to use [react-window](https://github.com/bvaughn/react-window) with the `List` component.
It renders 200 rows and can easily handle more.
Virtualization helps with performance issues.


The use of [react-window](https://github.com/bvaughn/react-window) when possible is encouraged.
If this library doesn't cover your use case, you should consider using alternatives like [react-virtuoso](https://github.com/petyosi/react-virtuoso).

## Customization

Here are some examples of customizing the component.
You can learn more about this in the
[overrides documentation page](/material-ui/customization/how-to-customize/).



# Dividers

---
productId: material-ui
title: React Divider component
components: Divider
githubLabel: 'scope: divider'
materialDesign: https://m2.material.io/components/dividers
githubSource: packages/mui-material/src/Divider
---

# Divider

The Divider component provides a thin, unobtrusive line for grouping elements to reinforce visual hierarchy.


## Introduction

The Material UI Divider component renders as a dark gray `<hr>` by default, and features several useful props for quick style adjustments.


## Basics

```jsx
import Divider from '@mui/material/Divider';
```

### Variants

The Divider component supports three variants: `fullWidth` (default), `inset`, and `middle`.


### Orientation

Use the `orientation` prop to change the Divider from horizontal to vertical. When using vertical orientation, the Divider renders a `<div>` with the corresponding accessibility attributes instead of `<hr>` to adhere to the WAI-ARIA [spec](https://www.w3.org/TR/wai-aria-1.2/#separator).


### Flex item

Use the `flexItem` prop to display the Divider when it's being used in a flex container.


### With children

Use the `textAlign` prop to align elements that are wrapped by the Divider.


## Customization

### Use with a List

When using the Divider to separate items in a List, use the `component` prop to render it as an `<li>`—otherwise it won't be a valid HTML element.


### Icon grouping

The demo below shows how to combine the props `variant="middle"` and `orientation="vertical"`.


## Accessibility

Due to its implicit role of `separator`, the Divider, which is a `<hr>` element, will be announced by screen readers as a "Horizontal Splitter" (or vertical, if you're using the `orientation` prop).

If you're using it as a purely stylistic element, we recommend setting `aria-hidden="true"` which will make screen readers bypass it.

```js
<Divider aria-hidden="true" />
```

If you're using the Divider to wrap other elements, such as text or chips, we recommend changing its rendered element to a plain `<div>` using the `component` prop, and setting `role="presentation"`.
This ensures that it's not announced by screen readers while still preserving the semantics of the elements inside it.

```js
<Divider component="div" role="presentation">
  <Typography>Text element</Typography>
</Divider>
```

## Anatomy

The Divider component is composed of a root `<hr>`.

```html
<hr class="MuiDivider-root">
  <!-- Divider children goes here -->
</hr>
```
