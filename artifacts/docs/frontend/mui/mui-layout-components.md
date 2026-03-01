---
title: Mui Layout Components
source: mui.com/material-ui
syllabus_weeks: [9]
topics: [Grid v2, Stack, Box, Container, responsive grid, spacing, offset, nested grid, flexbox]
---



# Grid

---
productId: system
title: React Grid component
githubLabel: 'component: Grid'
---

# Grid

The responsive layout grid adapts to screen size and orientation, ensuring consistency across layouts.


The `Grid` component works well for a layout with known columns. The columns can be configured in multiple breakpoints which you have to specify the column span of each child.

## How it works

The grid system is implemented with the `Grid` component:

- It uses [CSS's Flexible Box module](https://www.w3.org/TR/css-flexbox-1/) for high flexibility.
- The grid is always a flex item. Use the `container` prop to add flex container to it.
- Item widths are set in percentages, so they're always fluid and sized relative to their parent element.
- There are five default grid breakpoints: xs, sm, md, lg, and xl. If you need custom breakpoints, check out [custom breakpoints grid](#custom-breakpoints).
- Integer values can be given to each breakpoint, indicating how many of the 12 available columns are occupied by the component when the viewport width satisfies the [breakpoint constraints](/material-ui/customization/breakpoints/#default-breakpoints).
- It **does not** have the concept of rows. Meaning, you can't make the children span to multiple rows. If you need to do that, we recommend using [CSS Grid](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout) instead.
- It **does not** offer auto-placement children feature. It will try to fit the children one by one and if there is not enough space, the rest of the children will start on the next line and so on. If you need the auto-placement feature, we recommend using [CSS Grid](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout/Auto-placement) instead.

> **Warning:**
>
> The Grid component shouldn't be confused with a data grid; it is closer to a layout grid. For a data grid head to [the Data Grid component](/x/react-data-grid/).


## Fluid grids

Fluid grids use columns that scale and resize content. A fluid grid's layout can use breakpoints to determine if the layout needs to change dramatically.

### Basic grid

In order to create a grid layout, you need a container. Use `container` prop to create a grid container that wraps the grid items (the `Grid` is always an item).

Column widths are integer values between 1 and 12.
For example, an item with `size={6}` occupies half of the grid container's width.


### Multiple breakpoints

Components may have multiple widths defined, causing the layout to change at the defined breakpoint. Width values given to larger breakpoints override those given to smaller breakpoints.

For example, `size={{ xs: 12, sm: 6 }}` sizes a component to occupy half of the viewport width (6 columns) when viewport width is [600 or more pixels](/material-ui/customization/breakpoints/#default-breakpoints). For smaller viewports, the component fills all 12 available columns.


## Spacing

To control space between children, use the `spacing` prop.
The spacing value can be any positive number, including decimals and any string.
The prop is converted into a CSS property using the [`theme.spacing()`](/material-ui/customization/spacing/) helper.


### Row & column spacing

The `rowSpacing` and `columnSpacing` props allow for specifying the row and column gaps independently.
It's similar to the `row-gap` and `column-gap` properties of [CSS Grid](/system/grid/#row-gap-column-gap).


## Responsive values

You can switch the props' value based on the active breakpoint.
For instance, we can implement the [recommended](https://m2.material.io/design/layout/responsive-layout-grid.html) responsive layout grid of Material Design.


Responsive values is supported by:

- `size`
- `columns`
- `columnSpacing`
- `direction`
- `rowSpacing`
- `spacing`
- `offset`
- all the [other props](/system/properties/) of MUI System

## Auto-layout

The Auto-layout makes the _items_ equitably share the available space.
That also means you can set the width of one _item_ and the others will automatically resize around it.


### Variable width content

Set one of the size breakpoint props to `"auto"` to size a column based on the width of its content.


## Nested Grid

The grid container that renders inside another grid container is a nested grid which inherits the [`columns`](#columns) and [`spacing`](#spacing) from the top. The deep nested grid will inherit the props from the upper nested grid if it receives those props.


## Columns

You can change the default number of columns (12) with the `columns` prop.


## Offset

Move the item to the right by using the `offset` prop which can be:

- number, for example, `offset={{ md: 2 }}` - when used the item is moved to the right by 2 columns starts from `md` breakpoint and up.
- `"auto"` - when used, the item is moved to the right edge of the grid container.


## Custom breakpoints

If you specify custom breakpoints to the theme, you can use those names as grid item props in responsive values.


> **Info:**
>
> Custom breakpoints affect all [responsive values](#responsive-values).


### TypeScript

You have to set module augmentation on the theme breakpoints interface.

```ts
declare module '@mui/system' {
  interface BreakpointOverrides {
    // Your custom breakpoints
    laptop: true;
    tablet: true;
    mobile: true;
    desktop: true;
    // Remove default breakpoints
    xs: false;
    sm: false;
    md: false;
    lg: false;
    xl: false;
  }
}
```

## Limitations

### direction column and column-reverse

The `size` and `offset` props are **not supported** within `direction="column"` and `direction="column-reverse"` containers.

They define the number of grids the component will use for a given breakpoint. They are intended to control **width** using `flex-basis` in `row` containers but they will impact height in `column` containers.
If used, these props may have undesirable effects on the height of the `Grid` item elements.


# Stack

---
productId: system
title: React Stack component
components: Stack
githubLabel: 'component: Stack'
---

# Stack

Stack is a container component for arranging elements vertically or horizontally.

## Introduction

The Stack component manages the layout of its immediate children along the vertical or horizontal axis, with optional spacing and dividers between each child.

> **Info:**
>
> Stack is ideal for one-dimensional layouts, while Grid is preferable when you need both vertical _and_ horizontal arrangement.



## Basics

```jsx
import Stack from '@mui/system/Stack';
```

The Stack component acts as a generic container, wrapping around the elements to be arranged.

Use the `spacing` prop to control the space between children.
The spacing value can be any number, including decimals, or a string.
(The prop is converted into a CSS property using the [`theme.spacing()`](/material-ui/customization/spacing/) helper.)


### Stack vs. Grid

`Stack` is concerned with one-dimensional layouts, while [Grid](/system/react-grid/) handles two-dimensional layouts. The default direction is `column` which stacks children vertically.

## Direction

By default, Stack arranges items vertically in a column.
Use the `direction` prop to position items horizontally in a row:


## Dividers

Use the `divider` prop to insert an element between each child, as shown below:


## Responsive values

You can switch the `direction` or `spacing` values based on the active breakpoint.


## Flexbox gap

To use [flexbox `gap`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/gap) for the spacing implementation, set the `useFlexGap` prop to true.

It removes the [known limitations](#limitations) of the default implementation that uses CSS nested selector. However, CSS flexbox gap is not fully supported in some browsers.

We recommend checking the [support percentage](https://caniuse.com/?search=flex%20gap) before using it.


## Interactive demo

Below is an interactive demo that lets you explore the visual results of the different settings:


## System props

> **Info:**
>
> System props are deprecated and will be removed in the next major release. Please use the `sx` prop instead.
> 
> ```diff
> - <Stack mt={2} />
> + <Stack sx={{ mt: 2 }} />
> ```


## Limitations

### Margin on the children

Customizing the margin on the children is not supported by default.

For instance, the top-margin on the `button` component below will be ignored.

```jsx
<Stack>
  <button style={{ marginTop: '30px' }}>...</button>
</Stack>
```

> **Success:**
>
> To overcome this limitation, set [`useFlexGap`](#flexbox-gap) prop to true to switch to CSS flexbox gap implementation.
> 
> You can learn more about this limitation by visiting this [RFC](https://github.com/mui/material-ui/issues/33754).


### white-space: nowrap

The initial setting on flex items is `min-width: auto`.
This causes a positioning conflict when children use `white-space: nowrap;`.
You can reproduce the issue with:

```jsx
<Stack direction="row">
  <span style={{ whiteSpace: 'nowrap' }}>
```

In order for the item to stay within the container you need to set `min-width: 0`.

```jsx
<Stack direction="row" sx={{ minWidth: 0 }}>
  <span style={{ whiteSpace: 'nowrap' }}>
```

## Anatomy

The Stack component is composed of a single root `<div>` element:

```html
<div class="MuiStack-root">
  <!-- Stack contents -->
</div>
```


# Box

---
productId: system
title: React Box component
components: Box
githubLabel: 'component: Box'
---

<!-- This page's content is duplicated (with some product-specific details) across the Material UI, Joy UI, and MUI System docs. Any changes should be applied to all three pages at the same time. -->

# Box

The Box component is a generic, theme-aware container with access to CSS utilities from MUI System.


## Introduction

The Box component is a generic container for grouping other components.
It's a fundamental building block when working with MUI System—you can think of it as a `<div>` with extra built-in features, like access to your app's theme and the [`sx` prop](/system/getting-started/the-sx-prop/).

### Usage

The Box component differs from other containers available in MUI System in that its usage is intended to be multipurpose and open-ended, just like a `<div>`.
Components like [Container](/system/react-container/) and [Stack](/system/react-stack/), by contrast, feature usage-specific props that make them ideal for certain use cases: Container for main layout orientation, and Stack for one-dimensional layouts.

## Basics

```jsx
import Box from '@mui/system/Box';
```

The Box component renders as a `<div>` by default, but you can swap in any other valid HTML tag or React component using the `component` prop.
The demo below replaces the `<div>` with a `<section>` element:


## Customization

### With MUI System props

As a CSS utility component, the Box supports all [MUI System properties](/system/properties/).
You can use them as props directly on the component.


### With the sx prop

Use the [`sx` prop](/system/getting-started/the-sx-prop/) to quickly customize any Box instance using a superset of CSS that has access to all the style functions and theme-aware properties exposed in the MUI System package.
The demo below shows how to apply colors from the theme using this prop:


### Create your own Box

Use the `createBox()` utility to create your version of the Box component.
This is useful if you need to expose your container to a theme that's different from the default theme of the library you're working with:

```js
import { createBox, createTheme } from '@mui/system';

const defaultTheme = createTheme({
  // your custom theme values
});

const Box = createBox({ defaultTheme });

export default Box;
```

## Anatomy

The Box component is composed of a single root `<div>` element:

```html
<div className="MuiBox-root">
  <!-- contents of the Box -->
</div>
```


# Container

---
productId: system
title: React Container component
components: Container
githubLabel: 'component: Container'
---

# Container

The container centers your content horizontally. It's the most basic layout element.

While containers can be nested, most layouts do not require a nested container.


## Fluid

A fluid container width is bounded by the `maxWidth` prop value.


```jsx
<Container maxWidth="sm">
```

## Fixed

If you prefer to design for a fixed set of sizes instead of trying to accommodate a fully fluid viewport, you can set the `fixed` prop.
The max-width matches the min-width of the current breakpoint.


```jsx
<Container fixed>
```


# Grid

---
productId: material-ui
title: React Grid component
components: PigmentGrid, Grid
githubLabel: 'component: Grid'
materialDesign: https://m2.material.io/design/layout/understanding-layout.html
githubSource: packages/mui-material/src/Grid
---

# Grid

The responsive layout grid adapts to screen size and orientation, ensuring consistency across layouts.

The `Grid` component works well for a layout with a known number of columns.
The columns can be configured with multiple breakpoints to specify the column span of each child.


## How it works

The grid system is implemented with the `Grid` component:

- It uses [CSS Flexbox](https://www.w3.org/TR/css-flexbox-1/) (rather than CSS Grid) for high flexibility.
- The grid is always a flex item. Use the `container` prop to add a flex container.
- Item widths are set in percentages, so they're always fluid and sized relative to their parent element.
- There are five default grid breakpoints: xs, sm, md, lg, and xl. If you need custom breakpoints, check out [custom breakpoints grid](#custom-breakpoints).
- You can give integer values for each breakpoint, to indicate how many of the 12 available columns are occupied by the component when the viewport width satisfies the [breakpoint constraints](/material-ui/customization/breakpoints/#default-breakpoints).
- It uses [the `gap` CSS property](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/gap) to add spacing between items.
- It does _not_ support row spanning. Children elements cannot span multiple rows. We recommend using [CSS Grid](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout) if you need this functionality.
- It does _not_ automatically place children. It will try to fit the children one by one, and if there is not enough space, the rest of the children will start on the next line, and so on. If you need auto-placement, we recommend using [CSS Grid](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout/Auto-placement) instead.

> **Warning:**
>
> The `Grid` component is a _layout_ grid, not a _data_ grid.
> If you need a data grid, check out [the MUI X `DataGrid` component](/x/react-data-grid/).


## Fluid grids

Fluid grids use columns that scale and resize content. A fluid grid's layout can use breakpoints to determine if the layout needs to change dramatically.

### Basic grid

In order to create a grid layout, you need a container.
Use the `container` prop to create a grid container that wraps the grid items (the `Grid` is always an item).

Column widths are integer values between 1 and 12.
For example, an item with `size={6}` occupies half of the grid container's width.


### Multiple breakpoints

Items may have multiple widths defined, causing the layout to change at the defined breakpoint.
Width values apply to all wider breakpoints, and larger breakpoints override those given to smaller breakpoints.

For example, a component with `size={{ xs: 12, sm: 6 }}` occupies the entire viewport width when the viewport is [less than 600 pixels wide](/material-ui/customization/breakpoints/#default-breakpoints).
When the viewport grows beyond this size, the component occupies half of the total width—six columns rather than 12.


## Spacing

Use the `spacing` prop to control the space between children.
The spacing value can be any positive number (including decimals) or a string.
The prop is converted into a CSS property using the [`theme.spacing()`](/material-ui/customization/spacing/) helper.

The following demo illustrates the use of the `spacing` prop:


### Row and column spacing

The `rowSpacing` and `columnSpacing` props let you specify row and column gaps independently of one another.
They behave similarly to the `row-gap` and `column-gap` properties of [CSS Grid](/system/grid/#row-gap-column-gap).


## Responsive values

You can set prop values to change when a given breakpoint is active.
For instance, we can implement Material Design's [recommended](https://m2.material.io/design/layout/responsive-layout-grid.html) responsive layout grid, as seen in the following demo:


Responsive values are supported by:

- `size`
- `columns`
- `columnSpacing`
- `direction`
- `rowSpacing`
- `spacing`
- `offset`

## Interactive

Below is an interactive demo that lets you explore the visual results of the different settings:


## Auto-layout

The auto-layout feature gives equal space to all items present.
When you set the width of one item, the others will automatically resize to match it.


### Variable width content

When a breakpoint's value is given as `"auto"`, then a column's size will automatically adjust to match the width of its content.
The demo below shows how this works:


## Nested grid

The grid container that renders as a **direct child** inside another grid container is a nested grid that inherits its [`columns`](#columns) and [`spacing`](#spacing) from the top level.
It will also inherit the props of the top-level grid if it receives those props.

> **Success:**
>
> Note that a nested grid container should be a direct child of another grid container. If there are non-grid elements in between, the grid container will start as the new root container.
> 
> ```js
> <Grid container>
>   <Grid container> // A nested grid container that inherits columns and spacing from above.
>     <div>
>       <Grid container> // A new root grid container with its own variables scope.
> ```


### Inheriting spacing

A nested grid container inherits the row and column spacing from its parent unless the `spacing` prop is specified to the instance.


### Inheriting columns

A nested grid container inherits the columns from its parent unless the `columns` prop is specified to the instance.


## Columns

Use the `columns` prop to change the default number of columns (12) in the grid, as shown below:


## Offset

The `offset` prop pushes an item to the right side of the grid.
This props accepts:

- numbers—for example, `offset={{ md: 2 }}` pushes an item two columns to the right when the viewport size is equal to or greater than the `md` breakpoint.
- `"auto"`—this pushes the item to the far right side of the grid container.

The demo below illustrates how to use the offset props:


## Custom breakpoints

If you specify custom breakpoints in the theme, you can use those names as grid item props in responsive values:

```js
import { ThemeProvider, createTheme } from '@mui/material/styles';

function Demo() {
  return (
    <ThemeProvider
      theme={createTheme({
        breakpoints: {
          values: {
            laptop: 1024,
            tablet: 640,
            mobile: 0,
            desktop: 1280,
          },
        },
      })}
    >
      <Grid container spacing={{ mobile: 1, tablet: 2, laptop: 3 }}>
        {Array.from(Array(4)).map((_, index) => (
          <Grid key={index} size={{ mobile: 6, tablet: 4, laptop: 3 }}>
            <div>{index + 1}</div>
          </Grid>
        ))}
      </Grid>
    </ThemeProvider>
  );
}
```

> **Info:**
>
> Custom breakpoints affect all [responsive values](#responsive-values).


### TypeScript

You have to set module augmentation on the theme breakpoints interface.

```ts
declare module '@mui/system' {
  interface BreakpointOverrides {
    // Your custom breakpoints
    laptop: true;
    tablet: true;
    mobile: true;
    desktop: true;
    // Remove default breakpoints
    xs: false;
    sm: false;
    md: false;
    lg: false;
    xl: false;
  }
}
```

## Customization

### Centered elements

To center a grid item's content, specify `display="flex"` directly on the item.
Then use `justifyContent` and/or `alignItems` to adjust the position of the content, as shown below:


> **Warning:**
>
> Using the `container` prop does not work in this situation because the grid container is designed exclusively to wrap grid items.
> It cannot wrap other elements.


### Full border


### Half border


## Limitations

### Column direction

Using `direction="column"` or `direction="column-reverse"` is not supported.
The Grid component is specifically designed to subdivide a layout into columns, not rows.
You should not use the Grid component on its own to stack layout elements vertically.
Instead, you should use the [Stack component](/material-ui/react-stack/) inside of a Grid to create vertical layouts as shown below:



# Stack

---
productId: material-ui
title: React Stack component
components: Stack, PigmentStack
githubLabel: 'component: Stack'
githubSource: packages/mui-material/src/Stack
---

# Stack

Stack is a container component for arranging elements vertically or horizontally.

## Introduction

The Stack component manages the layout of its immediate children along the vertical or horizontal axis, with optional spacing and dividers between each child.

> **Info:**
>
> Stack is ideal for one-dimensional layouts, while Grid is preferable when you need both vertical _and_ horizontal arrangement.



## Basics

```jsx
import Stack from '@mui/material/Stack';
```

The Stack component acts as a generic container, wrapping around the elements to be arranged.

Use the `spacing` prop to control the space between children.
The spacing value can be any number, including decimals, or a string.
(The prop is converted into a CSS property using the [`theme.spacing()`](/material-ui/customization/spacing/) helper.)


### Stack vs. Grid

`Stack` is concerned with one-dimensional layouts, while [Grid](/material-ui/react-grid/) handles two-dimensional layouts. The default direction is `column` which stacks children vertically.

## Direction

By default, Stack arranges items vertically in a column.
Use the `direction` prop to position items horizontally in a row:


## Dividers

Use the `divider` prop to insert an element between each child.
This works particularly well with the [Divider](/material-ui/react-divider/) component, as shown below:


## Responsive values

You can switch the `direction` or `spacing` values based on the active breakpoint.


## Flexbox gap

To use [flexbox `gap`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/gap) for the spacing implementation, set the `useFlexGap` prop to true.

It removes the [known limitations](#limitations) of the default implementation that uses CSS nested selector. However, CSS flexbox gap is not fully supported in some browsers.

We recommend checking the [support percentage](https://caniuse.com/?search=flex%20gap) before using it.


To set the prop to all stack instances, create a theme with default props:

```js
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Stack from '@mui/material/Stack';

const theme = createTheme({
  components: {
    MuiStack: {
      defaultProps: {
        useFlexGap: true,
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Stack>…</Stack> {/* uses flexbox gap by default */}
    </ThemeProvider>
  );
}
```

## Interactive demo

Below is an interactive demo that lets you explore the visual results of the different settings:


## System props

> **Info:**
>
> System props are deprecated and will be removed in the next major release. Please use the `sx` prop instead.
> 
> ```diff
> - <Stack mt={2} />
> + <Stack sx={{ mt: 2 }} />
> ```


## Limitations

### Margin on the children

Customizing the margin on the children is not supported by default.

For instance, the top-margin on the `Button` component below will be ignored.

```jsx
<Stack>
  <Button sx={{ marginTop: '30px' }}>...</Button>
</Stack>
```

> **Success:**
>
> To overcome this limitation, set [`useFlexGap`](#flexbox-gap) prop to true to switch to CSS flexbox gap implementation.
> 
> You can learn more about this limitation by visiting this [RFC](https://github.com/mui/material-ui/issues/33754).


### white-space: nowrap

The initial setting on flex items is `min-width: auto`.
This causes a positioning conflict when children use `white-space: nowrap;`.
You can reproduce the issue with:

```jsx
<Stack direction="row">
  <Typography noWrap>
```

In order for the item to stay within the container you need to set `min-width: 0`.

```jsx
<Stack direction="row" sx={{ minWidth: 0 }}>
  <Typography noWrap>
```


## Anatomy

The Stack component is composed of a single root `<div>` element:

```html
<div class="MuiStack-root">
  <!-- Stack contents -->
</div>
```


# Box

---
productId: material-ui
title: React Box
components: Box
githubLabel: 'component: Box'
githubSource: packages/mui-material/src/Box
---

<!-- This page's content is duplicated (with some product-specific details) across the Material UI, Joy UI, and MUI System docs. Any changes should be applied to all three pages at the same time. -->

# Box

The Box component is a generic, theme-aware container with access to CSS utilities from MUI System.


## Introduction

The Box component is a generic container for grouping other components.
It's a fundamental building block when working with Material UI—you can think of it as a `<div>` with extra built-in features, like access to your app's theme and the [`sx` prop](/system/getting-started/the-sx-prop/).

### Usage

The Box component differs from other containers available in Material UI in that its usage is intended to be multipurpose and open-ended, just like a `<div>`.
Components like [Container](/material-ui/react-container/), [Stack](/material-ui/react-stack/) and [Paper](/material-ui/react-paper/), by contrast, feature usage-specific props that make them ideal for certain use cases: Container for main layout orientation, Stack for one-dimensional layouts, and Paper for elevated surfaces.

## Basics

```jsx
import Box from '@mui/material/Box';
```

The Box component renders as a `<div>` by default, but you can swap in any other valid HTML tag or React component using the `component` prop.
The demo below replaces the `<div>` with a `<section>` element:


## Customization

### With the sx prop

Use the [`sx` prop](/system/getting-started/the-sx-prop/) to quickly customize any Box instance using a superset of CSS that has access to all the style functions and theme-aware properties exposed in the MUI System package.
The demo below shows how to apply colors from the theme using this prop:


### With MUI System props

> **Info:**
>
> System props are deprecated and will be removed in the next major release. Please use the `sx` prop instead.
> 
> ```diff
> - <Box mt={2} />
> + <Box sx={{ mt: 2 }} />
> ```


## Anatomy

The Box component is composed of a single root `<div>` element:

```html
<div className="MuiBox-root">
  <!-- contents of the Box -->
</div>
```


# Container

---
productId: material-ui
title: React Container component
components: Container, PigmentContainer
githubLabel: 'component: Container'
githubSource: packages/mui-material/src/Container
---

# Container

The container centers your content horizontally. It's the most basic layout element.

While containers can be nested, most layouts do not require a nested container.


## Fluid

A fluid container width is bounded by the `maxWidth` prop value.


```jsx
<Container maxWidth="sm">
```

## Fixed

If you prefer to design for a fixed set of sizes instead of trying to accommodate a fully fluid viewport, you can set the `fixed` prop.
The max-width matches the min-width of the current breakpoint.


```jsx
<Container fixed>
```
