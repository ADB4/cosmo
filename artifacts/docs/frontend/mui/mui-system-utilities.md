---
title: Mui System Utilities
source: mui.com/material-ui
syllabus_weeks: [10]
topics: [system usage, borders, display, flexbox, grid, palette, sizing, spacing, typography, system properties]
---



# Usage

# Usage

Learn the basics of working with MUI System and its utilities.

## Why use MUI System?

MUI System's `sx` prop lets you avoid writing unnecessary styled-component code, and instead define styles directly within the component itself.
This is especially useful for one-off components with custom designs.

The following code samples illustrate the difference between styled-components and `sx`:


1. Using the styled-components API:

```jsx
const StatWrapper = styled('div')(
  ({ theme }) => `
  background-color: ${theme.palette.background.paper};
  box-shadow: ${theme.shadows[1]};
  border-radius: ${theme.shape.borderRadius}px;
  padding: ${theme.spacing(2)};
  min-width: 300px;
`,
);

const StatHeader = styled('div')(
  ({ theme }) => `
  color: ${theme.palette.text.secondary};
`,
);

const StyledTrend = styled(TrendingUpIcon)(
  ({ theme }) => `
  color: ${theme.palette.success.dark};
  font-size: 16px;
  vertical-alignment: sub;
`,
);

const StatValue = styled('div')(
  ({ theme }) => `
  color: ${theme.palette.text.primary};
  font-size: 34px;
  font-weight: ${theme.typography.fontWeightMedium};
`,
);

const StatDiff = styled('div')(
  ({ theme }) => `
  color: ${theme.palette.success.dark};
  display: inline;
  font-weight: ${theme.typography.fontWeightMedium};
  margin-left: ${theme.spacing(0.5)};
  margin-right: ${theme.spacing(0.5)};
`,
);

const StatPrevious = styled('div')(
  ({ theme }) => `
  color: ${theme.palette.text.secondary};
  display: inline;
  font-size: 12px;
`,
);

return (
  <StatWrapper>
    <StatHeader>Sessions</StatHeader>
    <StatValue>98.3 K</StatValue>
    <StyledTrend />
    <StatDiff>18.77%</StatDiff>
    <StatPrevious>vs last week</StatPrevious>
  </StatWrapper>
);
```

2. Using MUI System:

```jsx
<Box
  sx={{
    bgcolor: 'background.paper',
    boxShadow: 1,
    borderRadius: 1,
    p: 2,
    minWidth: 300,
  }}
>
  <Box sx={{ color: 'text.secondary' }}>Sessions</Box>
  <Box sx={{ color: 'text.primary', fontSize: 34, fontWeight: 'medium' }}>
    98.3 K
  </Box>
  <Box
    component={TrendingUpIcon}
    sx={{ color: 'success.dark', fontSize: 16, verticalAlign: 'sub' }}
  />
  <Box
    sx={{ color: 'success.dark', display: 'inline', fontWeight: 'medium', mx: 0.5 }}
  >
    18.77%
  </Box>
  <Box sx={{ color: 'text.secondary', display: 'inline', fontSize: 12 }}>
    vs. last week
  </Box>
</Box>
```

### The sx prop

MUI System's core utility is the `sx` prop, which gives you a quick and efficient way to apply the correct design tokens directly to a React element.

This prop provides a superset of CSS (that is it contains all CSS properties and selectors in addition to custom ones) that maps values directly from the theme, depending on the CSS property used.
It also simplifies the process of defining responsive values by referring to the breakpoints defined in the theme.

Visit [the `sx` prop page](/system/getting-started/the-sx-prop/) for complete details.

### Responsive demo

The following demo shows how to use the `sx` prop to apply custom styles and create a complex UI component using the `Box` wrapper alone.
Resize the window to see the responsive breakpoints:


## When to use MUI System

The `sx` prop is best suited for applying one-off styles to custom components.

This is in contrast to the styled-components API, which is ideal for building components that need to support a wide variety of contexts.
These components are used in many different parts of the application and support different combinations of props.

### Performance tradeoffs

MUI System relies on CSS-in-JS.
It works with both Emotion and styled-components.

#### Pros

- 📚 The `sx` prop uses a superset of CSS, so the syntax will be immediately familiar to you if you know CSS already.
  It also offers (optional) shorthand definitions that can save you time if you put in a little work to learn them upfront.
  These are documented in the **Style utilities** section of the primary navigation to the left.
- 📦 The System auto-purges, so that only the CSS that's used on the page is sent to the client.
  The initial bundle size cost is fixed—it doesn't get any larger as you add more CSS properties.
  You pay the cost of [@emotion/react](https://bundlephobia.com/package/@emotion/react) and [@mui/system](https://bundlephobia.com/package/@mui/system).
  The total size is ~15 kB gzipped.
  But if you are already using an MUI Core component library like Material UI, then it comes with no extra overhead.

#### Cons

Runtime performance takes a hit.

| Benchmark case                    | Code snippet          | Time normalized |
| :-------------------------------- | :-------------------- | --------------: |
| a. Render 1,000 primitives        | `<div className="…">` |           100ms |
| b. Render 1,000 components        | `<Div>`               |           112ms |
| c. Render 1,000 styled components | `<StyledDiv>`         |           181ms |
| d. Render 1,000 Box               | `<Box sx={…}>`        |           296ms |

<!-- #target-branch-reference -->

Visit the [benchmark folder](https://github.com/mui/material-ui/tree/master/benchmark/browser) for a reproduction of the metrics above.

We believe that for most use cases it's fast enough, but there are simple workarounds when performance becomes critical.
For instance, when rendering a list with many items, you can use a CSS child selector to have a single "style injection" point (using d. for the wrapper and a. for each item).

### API tradeoff

MUI System's unifying `sx` prop helps to maintain the separation of concerns between CSS utilities and component business logic.

For instance, a `color` prop on a button impacts multiple states (hover, focus, etc.), and is distinct from the CSS `color` property.

Only the `Box`, `Stack`, `Typography`, and `Grid` components accept MUI System properties as props for this reason.
These components are designed to solve CSS problems—they are CSS component utilities.

## Where to use MUI System

The `sx` prop can be used in four different locations:

### Core components

All Material UI and Joy UI components support the `sx` prop.

### Box

[`Box`](/system/react-box/) is a lightweight component that gives access to the `sx` prop, and can be used as a utility component, and as a wrapper for other components.
It renders a `<div>` element by default.

### Custom components

In addition to MUI System components, you can add the `sx` prop to your custom components too, by using the `styled` utility from `@mui/material/styles`.

```jsx
import { styled } from '@mui/material/styles';

const Div = styled('div')``;
```

### Any element with the babel plugin

Visit [the open GitHub issue](https://github.com/mui/material-ui/issues/23220) regarding this topic to learn more.

## How to use MUI System

### Design tokens in the theme

Visit the [System properties page](/system/properties/) to learn how the different CSS (and custom) properties are mapped to the theme keys.

### Shorthands

There are many shorthands available for various CSS properties.
These are documented on their respective Style utilities pages.
Here is an example of a few:

```jsx
<Box
  sx={{  boxShadow: 1, // theme.shadows[1]
    color: 'primary.main', // theme.palette.primary.main
    m: 1, // margin: theme.spacing(1)
    p: {
      xs: 1, // [theme.breakpoints.up('xs')]: { padding: theme.spacing(1) }
    },
    zIndex: 'tooltip', // theme.zIndex.tooltip
  }}
>
```

These shorthands are optional—they're great for saving time, but not necessary to use

### Superset of CSS

The `sx` prop supports CSS syntax including child and pseudo-selectors, media queries, raw CSS values, and more.
Here are a few examples of how you can implement these CSS features:

- Using pseudo-selectors:

  ```jsx
  <Box
    sx={{    // some styles
      ":hover": {
        boxShadow: 6,
      },
    }}
  >
  ```

- Using media queries:

  ```jsx
  <Box
    sx={{    // some styles
      '@media print': {
        width: 300,
      },
    }}
  >
  ```

- Using nested selector:

  ```jsx
  <Box
    sx={{    // some styles
      '& .ChildSelector': {
        bgcolor: 'primary.main',
      },
    }}
  >
  ```

### Responsive values

The `sx` prop simplifies the process of defining and implementing responsive breakpoints.
You can define a set of breakpoints in two different ways: as an object, or as an array.

#### Breakpoints as an object

The first option for breakpoints is to define them as an object, using the breakpoint values as keys.
Note that each property for a given breakpoint also applies to all larger breakpoints in the set.
For example, `width: { lg: 100 }` is equivalent to `theme.breakpoints.up('lg')`.

The following demo shows how to define a set of breakpoints using the object syntax:


> **Info:**
>
> 📣 Starting from v6, the object structure supports [container queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries) shorthand with `@`.
> 
> We recommend checking the [browser support](https://caniuse.com/?search=container%20que) before using CSS container queries.


The shorthand syntax is `@{breakpoint}/{container}`:

- **breakpoint**: a number for `px` unit or a breakpoint key (e.g. `sm`, `md`, `lg`, `xl` for default breakpoints) or a valid CSS value (e.g. `40em`).
- **container** (optional): the name of the [containment context](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries#naming_containment_contexts).


#### Breakpoints as an array

The second option is to define your breakpoints as an array, from smallest to largest.
Here's what that looks like:


> **Success:**
>
> This option should only be considered when the theme has a limited number of breakpoints, for example 3.
> 
> We recommend using the object API instead if you need to define more than a few breakpoints.


You can skip breakpoints with the `null` value:

```jsx
<Box sx={{ width: [null, null, 300] }}>This box has a responsive width.</Box>
```

#### Custom breakpoints

You can also specify your own custom breakpoints, and use them as keys when defining the breakpoints object.
Here is an example of how to do that:

```jsx
import * as React from 'react';
import Box from '@mui/material/Box';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  breakpoints: {
    values: {
      mobile: 0,
      tablet: 640,
      laptop: 1024,
      desktop: 1280,
    },
  },
});

export default function CustomBreakpoints() {
  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          width: {
            mobile: 100,
            laptop: 300,
          },
        }}
      >
        This box has a responsive width
      </Box>
    </ThemeProvider>
  );
}
```

If you are using TypeScript, you will also need to use [module augmentation](/material-ui/guides/typescript/#customization-of-theme) for the theme to accept the above values.

```ts
declare module '@mui/material/styles' {
  interface BreakpointOverrides {
    xs: false; // removes the `xs` breakpoint
    sm: false;
    md: false;
    lg: false;
    xl: false;
    tablet: true; // adds the `tablet` breakpoint
    laptop: true;
    desktop: true;
  }
}
```

#### Theme getter

If you wish to use the theme for a CSS property that is not supported natively by MUI System, then you can use a function as the value, in which you can access the theme object.
The following demo shows how this works:



# Borders

# Borders

Use border utilities to quickly style the border and border-radius of an element. Great for images, buttons, or any other element.

## Border

Use border utilities to add or remove an element's borders. Choose from all borders or one at a time.

### Additive


```jsx
<Box sx={{ border: 1 }}>…
<Box sx={{ borderTop: 1 }}>…
<Box sx={{ borderRight: 1 }}>…
<Box sx={{ borderBottom: 1 }}>…
<Box sx={{ borderLeft: 1 }}>…
```

### Subtractive


```jsx
<Box sx={{ border: 0 }}>…
<Box sx={{ borderTop: 0 }}>…
<Box sx={{ borderRight: 0 }}>…
<Box sx={{ borderBottom: 0 }}>…
<Box sx={{ borderLeft: 0 }}>…
```

## Border color


```jsx
<Box sx={{ borderColor: 'primary.main' }}>…
<Box sx={{ borderColor: 'secondary.main' }}>…
<Box sx={{ borderColor: 'error.main' }}>…
<Box sx={{ borderColor: 'grey.500' }}>…
<Box sx={{ borderColor: 'text.primary' }}>…
```

## Border-radius


```jsx
<Box sx={{ borderRadius: '50%' }}>…
<Box sx={{ borderRadius: 1 }}>… // theme.shape.borderRadius * 1
<Box sx={{ borderRadius: '16px' }}>…
```

## API

```js
import { borders } from '@mui/system';
```

| Import name         | Prop                | CSS property          | Theme key                                                                    |
| :------------------ | :------------------ | :-------------------- | :--------------------------------------------------------------------------- |
| `border`            | `border`            | `border`              | `borders`                                                                    |
| `borderTop`         | `borderTop`         | `border-top`          | `borders`                                                                    |
| `borderLeft`        | `borderLeft`        | `border-left`         | `borders`                                                                    |
| `borderRight`       | `borderRight`       | `border-right`        | `borders`                                                                    |
| `borderBottom`      | `borderBottom`      | `border-bottom`       | `borders`                                                                    |
| `borderColor`       | `borderColor`       | `border-color`        | [`palette`](/material-ui/customization/default-theme/?expand-path=$.palette) |
| `borderTopColor`    | `borderTopColor`    | `border-top-color`    | [`palette`](/material-ui/customization/default-theme/?expand-path=$.palette) |
| `borderRightColor`  | `borderRightColor`  | `border-right-color`  | [`palette`](/material-ui/customization/default-theme/?expand-path=$.palette) |
| `borderBottomColor` | `borderBottomColor` | `border-bottom-color` | [`palette`](/material-ui/customization/default-theme/?expand-path=$.palette) |
| `borderLeftColor`   | `borderLeftColor`   | `border-left-color`   | [`palette`](/material-ui/customization/default-theme/?expand-path=$.palette) |
| `borderRadius`      | `borderRadius`      | `border-radius`       | [`shape`](/material-ui/customization/default-theme/?expand-path=$.shape)     |


# Display

# Display

Quickly and responsively toggle the display, overflow, visibility, and more with the display utilities.

## Examples

### Inline


```jsx
<Box component="div" sx={{ display: 'inline' }}>inline</Box>
<Box component="div" sx={{ display: 'inline' }}>inline</Box>
```

### Block


```jsx
<Box component="span" sx={{ display: 'block' }}>block</Box>
<Box component="span" sx={{ display: 'block' }}>block</Box>
```

## Hiding elements

For faster mobile-friendly development, use responsive display classes for showing and hiding elements by device. Avoid creating entirely different versions of the same site, instead hide element responsively for each screen size.

| Screen Size        | Class                                                        |
| :----------------- | :----------------------------------------------------------- |
| Hidden on all      | `sx={{ display: 'none' }}`                                   |
| Hidden only on xs  | `sx={{ display: { xs: 'none', sm: 'block' } }}`              |
| Hidden only on sm  | `sx={{ display: { xs: 'block', sm: 'none', md: 'block' } }}` |
| Hidden only on md  | `sx={{ display: { xs: 'block', md: 'none', lg: 'block' } }}` |
| Hidden only on lg  | `sx={{ display: { xs: 'block', lg: 'none', xl: 'block' } }}` |
| Hidden only on xl  | `sx={{ display: { xs: 'block', xl: 'none' } }}`              |
| Visible only on xs | `sx={{ display: { xs: 'block', sm: 'none' } }}`              |
| Visible only on sm | `sx={{ display: { xs: 'none', sm: 'block', md: 'none' } }}`  |
| Visible only on md | `sx={{ display: { xs: 'none', md: 'block', lg: 'none' } }}`  |
| Visible only on lg | `sx={{ display: { xs: 'none', lg: 'block', xl: 'none' } }}`  |
| Visible only on xl | `sx={{ display: { xs: 'none', xl: 'block' } }}`              |


```jsx
<Box sx={{ display: { xs: 'block', md: 'none' }}}>
  hide on screens wider than md
</Box>
<Box sx={{ display: { xs: 'none', md: 'block' }}}>
  hide on screens smaller than md
</Box>
```

## Display in print


```jsx
<Box sx={{ display: 'block', displayPrint: 'none' }}>
  Screen Only (Hide on print only)
</Box>
<Box sx={{ display: 'none', displayPrint: 'block' }}>
  Print Only (Hide on screen only)
</Box>
```

## Overflow


```jsx
<Box component="div" sx={{ overflow: 'hidden' }}>
  Not scrollable, overflow is hidden
</Box>
<Box component="div" sx={{ overflow: 'auto' }}>
  Try scrolling this overflow auto box
</Box>
```

## Text overflow


```jsx
<Box component="div" sx={{ textOverflow: 'clip' }}>
  Lorem Ipsum is simply dummy text
</Box>
<Box component="div" sx={{ textOverflow: 'ellipsis' }}>
  Lorem Ipsum is simply dummy text
</Box>
```

## Visibility


```jsx
<Box component="div" sx={{ visibility: 'visible' }}>
  Visible container
</Box>
<Box component="div" sx={{ visibility: 'hidden' }}>
  Invisible container
</Box>
```

## White space


```jsx
<Box component="div" sx={{ whiteSpace: 'nowrap' }}>
  Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.
</Box>
<Box component="div" sx={{ whiteSpace: 'normal' }}>
  Lorem Ipsum has been the industry's standard dummy text ever since the 1500s.
</Box>
```

## API

```js
import { display } from '@mui/system';
```

| Import name    | Prop           | CSS property    | Theme key |
| :------------- | :------------- | :-------------- | :-------- |
| `displayPrint` | `displayPrint` | `display`       | none      |
| `displayRaw`   | `display`      | `display`       | none      |
| `overflow`     | `overflow`     | `overflow`      | none      |
| `textOverflow` | `textOverflow` | `text-overflow` | none      |
| `visibility`   | `visibility`   | `visibility`    | none      |
| `whiteSpace`   | `whiteSpace`   | `white-space`   | none      |


# Flexbox

# Flexbox

Quickly manage the layout, alignment, and sizing of grid columns, navigation, components, and more with a full suite of responsive flexbox utilities.

If you are **new to or unfamiliar with flexbox**, we encourage you to read this [CSS-Tricks flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/) guide.

## Properties for the Parent

### display


```jsx
<Box sx={{ display: 'flex' }}>…
<Box sx={{ display: 'inline-flex' }}>…
```

### flex-direction

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/flex-direction" target="_blank" rel="noopener">flex-direction</a>
on MDN.


```jsx
<Box sx={{ flexDirection: 'row' }}>…
<Box sx={{ flexDirection: 'row-reverse' }}>…
<Box sx={{ flexDirection: 'column' }}>…
<Box sx={{ flexDirection: 'column-reverse' }}>…
```

### flex-wrap

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/flex-wrap" target="_blank" rel="noopener">flex-wrap</a>
on MDN.


```jsx
<Box sx={{ flexWrap: 'nowrap' }}>…
<Box sx={{ flexWrap: 'wrap' }}>…
<Box sx={{ flexWrap: 'wrap-reverse' }}>…
```

### justify-content

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/justify-content" target="_blank" rel="noopener">justify-content</a>
on MDN.


```jsx
<Box sx={{ justifyContent: 'flex-start' }}>…
<Box sx={{ justifyContent: 'flex-end' }}>…
<Box sx={{ justifyContent: 'center' }}>…
<Box sx={{ justifyContent: 'space-between' }}>…
<Box sx={{ justifyContent: 'space-around' }}>…
<Box sx={{ justifyContent: 'space-evenly' }}>…
```

### align-items

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/align-items" target="_blank" rel="noopener">align-items</a>
on MDN.


```jsx
<Box sx={{ alignItems: 'flex-start' }}>…
<Box sx={{ alignItems: 'flex-end' }}>…
<Box sx={{ alignItems: 'center' }}>…
<Box sx={{ alignItems: 'stretch' }}>…
<Box sx={{ alignItems: 'baseline' }}>…
```

### align-content

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/align-content" target="_blank" rel="noopener">align-content</a>
on MDN.


```jsx
<Box sx={{ alignContent: 'flex-start' }}>…
<Box sx={{ alignContent: 'flex-end' }}>…
<Box sx={{ alignContent: 'center' }}>…
<Box sx={{ alignContent: 'space-between' }}>…
<Box sx={{ alignContent: 'space-around' }}>…
<Box sx={{ alignContent: 'stretch' }}>…
```

## Properties for the Children

### order

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/order" target="_blank" rel="noopener">order</a>
on MDN.


```jsx
<Box sx={{ order: 2 }}>Item 1</Box>
<Box sx={{ order: 3 }}>Item 2</Box>
<Box sx={{ order: 1 }}>Item 3</Box>
```

### flex-grow

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/flex-grow" target="_blank" rel="noopener">flex-grow</a>
on MDN.


```jsx
<Box sx={{ flexGrow: 1 }}>Item 1</Box>
<Box>Item 2</Box>
<Box>Item 3</Box>
```

### flex-shrink

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/flex-shrink" target="_blank" rel="noopener">flex-shrink</a>
on MDN.


```jsx
<Box sx={{ width: '100%' }}>Item 1</Box>
<Box sx={{ flexShrink: 1 }}>Item 2</Box>
<Box sx={{ flexShrink: 0 }}>Item 3</Box>
```

### align-self

For more information please see
<a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/align-self" target="_blank" rel="noopener">align-self</a>
on MDN.


```jsx
<Box>Item 1</Box>
<Box sx={{ alignSelf: 'flex-end' }}>Item 2</Box>
<Box>Item 3</Box>
```

## API

```js
import { flexbox } from '@mui/system';
```

| Import name      | Prop             | CSS property      | Theme key |
| :--------------- | :--------------- | :---------------- | :-------- |
| `flexDirection`  | `flexDirection`  | `flex-direction`  | none      |
| `flexWrap`       | `flexWrap`       | `flex-wrap`       | none      |
| `justifyContent` | `justifyContent` | `justify-content` | none      |
| `alignItems`     | `alignItems`     | `align-items`     | none      |
| `alignContent`   | `alignContent`   | `align-content`   | none      |
| `order`          | `order`          | `order`           | none      |
| `flex`           | `flex`           | `flex`            | none      |
| `flexGrow`       | `flexGrow`       | `flex-grow`       | none      |
| `flexShrink`     | `flexShrink`     | `flex-shrink`     | none      |
| `alignSelf`      | `alignSelf`      | `align-self`      | none      |


# Grid

# CSS Grid

Quickly manage the layout, alignment, and sizing of grid columns, navigation, components, and more with a full suite of responsive grid utilities.

If you are **new to or unfamiliar with grid**, you're encouraged to read this [CSS-Tricks grid](https://css-tricks.com/snippets/css/complete-guide-grid/) guide.

## Properties for the parent

### display

To define a `grid` container, you must specify the `display` CSS property to have one of the values: `grid` or `inline-grid`.


```jsx
<Box sx={{ display: 'grid' }}>…</Box>
<Box sx={{ display: 'inline-grid' }}>…</Box>
```

### grid-template-rows

The `grid-template-rows` property defines the line names and track sizing functions of the grid rows.


### grid-template-columns

The `grid-template-columns` property defines the line names and track sizing functions of the grid columns.


### gap

The `gap: size` property specifies the gap between the different items inside the CSS grid.


### row-gap & column-gap

The `row-gap` and `column-gap` CSS properties allow for specifying the row and column gaps independently.


### grid-template-areas

The `grid-template-area` property defines a grid template by referencing the names of the grid areas which are specified with the `grid-area` property.


### grid-auto-columns

The `grid-auto-column` property specifies the size of an implicitly-created grid column track or pattern of tracks.


On the demo above, the second non-visible column has a width of `1fr`/4 which is approximately equal to `25%`.

### grid-auto-rows

The `grid-auto-rows` property specifies the size of an implicitly-created grid row track or pattern of tracks.


### grid-auto-flow

The `grid-auto-flow` property controls how the auto-placement algorithm works, specifying exactly how auto-placed items get flowed into the grid.


## Properties for the children

### grid-column

The `grid-column` property is a shorthand for `grid-column-start` + `grid-column-end`. You can see how it's used in the [grid-auto-columns example](/system/grid/#grid-auto-columns).

You can either set the start and end line:

```jsx
<Box sx={{ gridColumn: '1 / 3' }}>…
```

Or set the number of columns to span:

```jsx
<Box sx={{ gridColumn: 'span 2' }}>…
```

### grid-row

The `grid-row` property is a shorthand for `grid-row-start` + `grid-row-end`. You can see how it's used in the [grid-auto-rows example](/system/grid/#grid-auto-rows).

You can either set the start and end line:

```jsx
<Box sx={{ gridRow: '1 / 3' }}>…
```

Or set the number of rows to span:

```jsx
<Box sx={{ gridRow: 'span 2' }}>…
```

### grid-area

The `grid-area` property allows you to give an item a name so that it can be referenced by a template created with the `grid-template-areas` property. You can see how it's used in the [grid-template-area example](/system/grid/#grid-template-areas).

```jsx
<Box sx={{ gridArea: 'header' }}>…
```

## API

```js
import { grid } from '@mui/system';
```

| Import name           | Prop                  | CSS property            | Theme key |
| :-------------------- | :-------------------- | :---------------------- | :-------- |
| `gap`                 | `gap`                 | `gap`                   | none      |
| `columnGap`           | `columnGap`           | `column-gap`            | none      |
| `rowGap`              | `rowGap`              | `row-gap`               | none      |
| `gridColumn`          | `gridColumn`          | `grid-column`           | none      |
| `gridRow`             | `gridRow`             | `grid-row`              | none      |
| `gridAutoFlow`        | `gridAutoFlow`        | `grid-auto-flow`        | none      |
| `gridAutoColumns`     | `gridAutoColumns`     | `grid-auto-columns`     | none      |
| `gridAutoRows`        | `gridAutoRows`        | `grid-auto-rows`        | none      |
| `gridTemplateColumns` | `gridTemplateColumns` | `grid-template-columns` | none      |
| `gridTemplateRows`    | `gridTemplateRows`    | `grid-template-rows`    | none      |
| `gridTemplateAreas`   | `gridTemplateAreas`   | `grid-template-areas`   | none      |
| `gridArea`            | `gridArea`            | `grid-area`             | none      |


# Palette

# Palette

Convey meaning through color with a handful of color utility classes. Includes support for styling links with hover states, too.

## Color


```jsx
<Box sx={{ color: 'primary.main' }}>…
<Box sx={{ color: 'secondary.main' }}>…
<Box sx={{ color: 'error.main' }}>…
<Box sx={{ color: 'warning.main' }}>…
<Box sx={{ color: 'info.main' }}>…
<Box sx={{ color: 'success.main' }}>…
<Box sx={{ color: 'text.primary' }}>…
<Box sx={{ color: 'text.secondary' }}>…
<Box sx={{ color: 'text.disabled' }}>…
```

## Background color


```jsx
<Box sx={{ bgcolor: 'primary.main' }}>…
<Box sx={{ bgcolor: 'secondary.main' }}>…
<Box sx={{ bgcolor: 'error.main' }}>…
<Box sx={{ bgcolor: 'warning.main' }}>…
<Box sx={{ bgcolor: 'info.main' }}>…
<Box sx={{ bgcolor: 'success.main' }}>…
<Box sx={{ bgcolor: 'text.primary' }}>…
<Box sx={{ bgcolor: 'text.secondary' }}>…
<Box sx={{ bgcolor: 'text.disabled' }}>…
```

## API

```js
import { palette } from '@mui/system';
```

| Import name | Prop      | CSS property      | Theme key                                                                    |
| :---------- | :-------- | :---------------- | :--------------------------------------------------------------------------- |
| `color`     | `color`   | `color`           | [`palette`](/material-ui/customization/default-theme/?expand-path=$.palette) |
| `bgcolor`   | `bgcolor` | `backgroundColor` | [`palette`](/material-ui/customization/default-theme/?expand-path=$.palette) |


# Sizing

# Sizing

Easily make an element as wide or as tall (relative to its parent) with the width and height utilities.

## Supported values

The sizing properties: `width`, `height`, `minHeight`, `maxHeight`, `minWidth`, and `maxWidth` are using the following custom transform function for the value:

```js
function transform(value) {
  return value <= 1 && value !== 0 ? `${value * 100}%` : value;
}
```

If the value is between (0, 1], it's converted to percent.
Otherwise, it is directly set on the CSS property.


```jsx
<Box sx={{ width: 1/4 }}> // Equivalent to width: '25%'
<Box sx={{ width: 300 }}> // Numbers are converted to pixel values.
<Box sx={{ width: '75%' }}> // String values are used as raw CSS.
<Box sx={{ width: 1 }}> // 100%
```

## Width


```jsx
<Box sx={{ width: '25%' }}>…
<Box sx={{ width: '50%' }}>…
<Box sx={{ width: '75%' }}>…
<Box sx={{ width: '100%' }}>…
<Box sx={{ width: 'auto' }}>…
```

### Max-width

The max-width property allows setting a constraint on your breakpoints.
In this example, the value resolves to [`theme.breakpoints.values.md`](/material-ui/customization/default-theme/?expand-path=$.breakpoints.values).

```jsx
<Box sx={{ maxWidth: 'md' }}>…
```

## Height


```jsx
<Box sx={{ height: '25%' }}>…
<Box sx={{ height: '50%' }}>…
<Box sx={{ height: '75%' }}>…
<Box sx={{ height: '100%' }}>…
```

## API

```js
import { sizing } from '@mui/system';
```

| Import name | Prop        | CSS property | Theme key                                                                                                |
| :---------- | :---------- | :----------- | :------------------------------------------------------------------------------------------------------- |
| `width`     | `width`     | `width`      | none                                                                                                     |
| `maxWidth`  | `maxWidth`  | `max-width`  | [`theme.breakpoints.values`](/material-ui/customization/default-theme/?expand-path=$.breakpoints.values) |
| `minWidth`  | `minWidth`  | `min-width`  | none                                                                                                     |
| `height`    | `height`    | `height`     | none                                                                                                     |
| `maxHeight` | `maxHeight` | `max-height` | none                                                                                                     |
| `minHeight` | `minHeight` | `min-height` | none                                                                                                     |
| `boxSizing` | `boxSizing` | `box-sizing` | none                                                                                                     |


# Spacing

# Spacing

A wide range of shorthand responsive margin and padding utility classes to modify an element's appearance.

## Notation

The space utility converts shorthand margin and padding props to margin and padding CSS declarations. The props are named using the format `{property}{sides}`.

Where _property_ is one of:

- `m` - for classes that set _margin_
- `p` - for classes that set _padding_

Where _sides_ is one of:

- `t` - for classes that set _margin-top_ or _padding-top_
- `b` - for classes that set _margin-bottom_ or _padding-bottom_
- `l` - for classes that set _margin-left_ or _padding-left_
- `r` - for classes that set _margin-right_ or _padding-right_
- `x` - for classes that set both _\*-left_ and _\*-right_
- `y` - for classes that set both _\*-top_ and _\*-bottom_
- blank - for classes that set a margin or padding on all 4 sides of the element

## Transformation

Depending on the input and the theme configuration, the following transformation is applied:

- input: `number` & theme: `number`: the prop value is multiplied by the theme value.

```jsx
const theme = {
  spacing: 8,
}

<Box sx={{ m: -2 }} /> // margin: -16px;
<Box sx={{ m: 0 }} /> // margin: 0px;
<Box sx={{ m: 0.5 }} /> // margin: 4px;
<Box sx={{ m: 2 }} /> // margin: 16px;
```

- input: `number` & theme: `array`: the prop value is used as the array index.

```jsx
const theme = {
  spacing: [0, 2, 3, 5, 8],
}

<Box sx={{ m: -2 }} /> // margin: -3px;
<Box sx={{ m: 0 }} /> // margin: 0px;
<Box sx={{ m: 2 }} /> // margin: 3px;
```

- input: `number` & theme: `function`: the function is called with the prop value.

```jsx
const theme = {
  spacing: value => value * 2,
}

<Box sx={{ m: 0 }} /> // margin: 0px;
<Box sx={{ m: 2 }} /> // margin: 4px;
```

- input: `string`: the prop value is passed as raw CSS value.

```jsx
<Box sx={{ m: '2rem' }} /> // margin: 2rem;
<Box sx={{ mx: 'auto' }} /> // margin-left: auto; margin-right: auto;
```

## Example


```jsx
<Box sx={{ p: 1 }}>…
<Box sx={{ m: 1 }}>…
<Box sx={{ p: 2 }}>…
```

## Horizontal centering

The CSS flex and grid display properties are often used to align elements at the center.
However, you can also use `margin-left: auto;`, `margin-right: auto;`, and a width for horizontally centering:


```jsx
<Box sx={{ mx: 'auto', width: 200 }}>…
```

## API

```js
import { spacing } from '@mui/system';
```

| Import name | Prop | CSS property                    | Theme key                                                                    |
| :---------- | :--- | :------------------------------ | :--------------------------------------------------------------------------- |
| `spacing`   | `m`  | `margin`                        | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `mt` | `margin-top`                    | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `mr` | `margin-right`                  | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `mb` | `margin-bottom`                 | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `ml` | `margin-left`                   | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `mx` | `margin-left`, `margin-right`   | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `my` | `margin-top`, `margin-bottom`   | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `p`  | `padding`                       | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `pt` | `padding-top`                   | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `pr` | `padding-right`                 | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `pb` | `padding-bottom`                | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `pl` | `padding-left`                  | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `px` | `padding-left`, `padding-right` | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |
| `spacing`   | `py` | `padding-top`, `padding-bottom` | [`spacing`](/material-ui/customization/default-theme/?expand-path=$.spacing) |

_Some people find the prop shorthand confusing, you can use the full version if you prefer:_

```diff
-<Box sx={{ pt: 2 }} />
+<Box sx={{ paddingTop: 2 }} />
```

```diff
-<Box sx={{ px: 2 }} />
+<Box sx={{ paddingX: 2 }} />
```


# Typography

# Typography

Documentation and examples for common text utilities to control alignment, wrapping, weight, and more.

## Variant


```jsx
<Box sx={{ typography: 'subtitle2' }}>… // theme.typography.subtitle2
<Box sx={{ typography: 'body1' }}>…
<Box sx={{ typography: 'body2' }}>…
```

## Text alignment


```jsx
<Box sx={{ textAlign: 'left' }}>…
<Box sx={{ textAlign: 'center' }}>…
<Box sx={{ textAlign: 'right' }}>…
```

## Text transformation


```jsx
<Box sx={{ textTransform: 'capitalize' }}>…
<Box sx={{ textTransform: 'lowercase' }}>…
<Box sx={{ textTransform: 'uppercase' }}>…
```

## Font weight


```jsx
<Box sx={{ fontWeight: 'light' }}>… // theme.typography.fontWeightLight
<Box sx={{ fontWeight: 'regular' }}>…
<Box sx={{ fontWeight: 'medium' }}>…
<Box sx={{ fontWeight: 500 }}>…
<Box sx={{ fontWeight: 'bold' }}>…
```

## Font size


```jsx
<Box sx={{ fontSize: 'default' }}>…  // theme.typography.fontSize
<Box sx={{ fontSize: 'h6.fontSize' }}>…
<Box sx={{ fontSize: 16 }}>…
```

## Font style


```jsx
<Box sx={{ fontStyle: 'normal' }}>…
<Box sx={{ fontStyle: 'italic' }}>…
<Box sx={{ fontStyle: 'oblique' }}>…
```

## Font family


```jsx
<Box sx={{ fontFamily: 'default' }}>…
<Box sx={{ fontFamily: 'Monospace' }}>…
```

## Letter spacing


```jsx
<Box sx={{ letterSpacing: 6 }}>…
<Box sx={{ letterSpacing: 10 }}>…
```

## Line height


```jsx
<Box sx={{ lineHeight: 'normal' }}>…
<Box sx={{ lineHeight: 10 }}>…
```

## API

```js
import { typography } from '@mui/system';
```

| Import name     | Prop            | CSS property                                                                                 | Theme key                                                                          |
| :-------------- | :-------------- | :------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| `typography`    | `typography`    | `font-family`, `font-weight`, `font-size`, `line-height`, `letter-spacing`, `text-transform` | [`typography`](/material-ui/customization/default-theme/?expand-path=$.typography) |
| `fontFamily`    | `fontFamily`    | `font-family`                                                                                | [`typography`](/material-ui/customization/default-theme/?expand-path=$.typography) |
| `fontSize`      | `fontSize`      | `font-size`                                                                                  | [`typography`](/material-ui/customization/default-theme/?expand-path=$.typography) |
| `fontStyle`     | `fontStyle`     | `font-style`                                                                                 | [`typography`](/material-ui/customization/default-theme/?expand-path=$.typography) |
| `fontWeight`    | `fontWeight`    | `font-weight`                                                                                | [`typography`](/material-ui/customization/default-theme/?expand-path=$.typography) |
| `letterSpacing` | `letterSpacing` | `letter-spacing`                                                                             | none                                                                               |
| `lineHeight`    | `lineHeight`    | `line-height`                                                                                | none                                                                               |
| `textAlign`     | `textAlign`     | `text-align`                                                                                 | none                                                                               |
| `textTransform` | `textTransform` | `text-transform`                                                                             | none                                                                               |
