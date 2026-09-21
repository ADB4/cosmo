---
title: Mui Sx Prop
source: mui.com/material-ui
syllabus_weeks: [10]
topics: [sx prop, theme-aware properties, responsive values, callback values, array values, performance, TypeScript, nesting, shorthand]
---



# The Sx Prop

# The sx prop

The sx prop is a shortcut for defining custom styles that have access to the theme.

The `sx` prop lets you work with a superset of CSS that packages all of the style functions exposed in `@mui/system`.
You can specify any valid CSS using this prop, as well as many _theme-aware_ properties that are unique to MUI System.

## Basic example

The following demo illustrates how to work with the `sx` prop.
Note that not all of the values are valid CSS properties—that's because the `sx` keys are mapped to specific properties of the theme.
The rest of this document explores this concept in more detail.


## Theme-aware properties

### Borders

The `border` property can only receive a number as a value.
It creates a solid black border using the number to define the width in pixels:

```jsx
<Box sx={{ border: 1 }} />
// equivalent to border: '1px solid black'
```

The `borderColor` property can receive a string, which represents the path in `theme.palette`:

```jsx
<Box sx={{ borderColor: 'primary.main' }} />
// equivalent to borderColor: theme => theme.palette.primary.main
```

The `borderRadius` property multiplies the value it receives by the `theme.shape.borderRadius` value (the default for this value is `4px`).

```jsx
<Box sx={{ borderRadius: 2 }} />
// equivalent to borderRadius: theme => 2 * theme.shape.borderRadius
```

Read more on the [Borders page](/system/borders/).

### Display

The `displayPrint` property allows you to specify a CSS `display` value that will only be applied when printing:

```jsx
<Box sx={{ displayPrint: 'none' }} /> // equivalent to '@media print': { display: 'none' }
```

Read more on the [Display page](/system/display/).

### Grid

The CSS Grid properties `gap`, `rowGap` and `columnGap` multiply the values they receive by the `theme.spacing` value (the default for the value is `8px`).

```jsx
<Box sx={{ gap: 2 }} />
// equivalent to gap: theme => theme.spacing(2)
```

Read more on the [Grid page](/system/grid/).

### Palette

The `color` and `backgroundColor` properties can receive a string, which represents the path in `theme.palette`:

```jsx
<Box sx={{ color: 'primary.main' }} />
// equivalent to color: theme => theme.palette.primary.main
```

The `backgroundColor` property is also available through its alias `bgcolor`:

```jsx
<Box sx={{ bgcolor: 'primary.main' }} />
// equivalent to backgroundColor: theme => theme.palette.primary.main
```

Read more on the [Palette page](/system/palette/).

### Positions

The `zIndex` property maps its value to the `theme.zIndex` value:

```jsx
<Box sx={{ zIndex: 'tooltip' }} />
// equivalent to zIndex: theme => theme.zIndex.tooltip
```

Read more on the [Positions page](/system/positions/).

### Shadows

The `boxShadow` property maps its value to the `theme.shadows` value:

```jsx
<Box sx={{ boxShadow: 1 }} />
// equivalent to boxShadow: theme => theme.shadows[1]
```

Read more on the [Shadows page](/system/shadows/).

### Sizing

The sizing properties `width`, `height`, `minHeight`, `maxHeight`, `minWidth`, and `maxWidth` use the following custom transform function for the value:

```js
function transform(value) {
  return value <= 1 && value !== 0 ? `${value * 100}%` : value;
}
```

If the value is between (0, 1], it's converted to a percentage.
Otherwise, it is directly set on the CSS property:

```jsx
<Box sx={{ width: 1/2 }} /> // equivalent to width: '50%'
<Box sx={{ width: 20 }} /> // equivalent to width: '20px'
```

Read more on the [Sizing page](/system/sizing/).

### Spacing

The spacing properties `margin`, `padding`, and the corresponding longhand properties multiply the values they receive by the `theme.spacing` value (the default for the value is `8px`):

```jsx
<Box sx={{ margin: 2 }} />
// equivalent to margin: theme => theme.spacing(2)
```

The following aliases are available for the spacing properties:

| Prop | CSS property                    |
| :--- | :------------------------------ |
| `m`  | `margin`                        |
| `mt` | `margin-top`                    |
| `mr` | `margin-right`                  |
| `mb` | `margin-bottom`                 |
| `ml` | `margin-left`                   |
| `mx` | `margin-left`, `margin-right`   |
| `my` | `margin-top`, `margin-bottom`   |
| `p`  | `padding`                       |
| `pt` | `padding-top`                   |
| `pr` | `padding-right`                 |
| `pb` | `padding-bottom`                |
| `pl` | `padding-left`                  |
| `px` | `padding-left`, `padding-right` |
| `py` | `padding-top`, `padding-bottom` |

Read more on the [Spacing page](/system/spacing/).

### Typography

The `fontFamily`, `fontSize`, `fontStyle`, `fontWeight` properties map their value to the `theme.typography` value:

```jsx
<Box sx={{ fontWeight: 'fontWeightLight' }} />
// equivalent to fontWeight: theme.typography.fontWeightLight
```

The same can be achieved by omitting the CSS property prefix `fontWeight`:

```jsx
<Box sx={{ fontWeight: 'light' }} />
// equivalent to fontWeight: theme.typography.fontWeightLight
```

There is an additional `typography` prop available, which sets all values defined in the specific `theme.typography` variant:

```jsx
<Box sx={{ typography: 'body1' }} />
// equivalent to { ...theme.typography.body1 }
```

Read more on the [Typography page](/system/typography/).

## Responsive values

All properties associated with the `sx` prop also support responsive values for specific breakpoints and container queries.

Read more on the [Usage page—Responsive values](/system/getting-started/usage/#responsive-values).

## Callback values

Use a callback when you need to get theme values that are objects:

```jsx
<Box
  sx={(theme) => ({
    ...theme.typography.body,
    color: theme.palette.primary.main,
  })}
/>
```

> **Info:**
>
> Callback as a value has been deprecated.
> Please use the callback as the entire value instead.
> 
> ```diff
> - sx={{ height: (theme) => theme.spacing(10) }}
> + sx={(theme) => ({ height: theme.spacing(10) })}
> ```
> 
> <br />
> You can migrate the code using our codemod:
> 
> ```bash
> npx @mui/codemod@latest v6.0.0/sx-prop path/to/file-or-folder
> ```


In TypeScript, to use custom theme properties with the `sx` prop callback, extend the `Theme` type from the `@mui/system` library using [module augmentation](https://www.typescriptlang.org/docs/handbook/declaration-merging.html#module-augmentation):

```tsx
import * as React from 'react';
import Box from '@mui/material/Box';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { orange } from '@mui/material/colors';

declare module '@mui/system' {
  interface Theme {
    status: {
      warning: string;
    };
  }
}

const theme = createTheme({
  status: {
    warning: orange[500],
  },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={(theme) => ({
          bgcolor: theme.status.warning,
        })}
      >
        Example
      </Box>
    </ThemeProvider>
  );
}
```

## Array values

Array types are useful when you want to partially override some styles in the former index:

```jsx
<Box
  sx={[
    {
      '&:hover': {
        color: 'red',
        backgroundColor: 'white',
      },
    },
    foo && {
      '&:hover': { backgroundColor: 'grey' },
    },
    bar && {
      '&:hover': { backgroundColor: 'yellow' },
    },
  ]}
/>
```

When you hover on this element, `color: red; backgroundColor: white;` is applied.

If `foo: true`, then `color: red; backgroundColor: grey;` is applied when hovering.

If `bar: true`, then `color: red; backgroundColor: yellow;` is applied when hovering regardless of `foo` value, because the higher index of the array has higher specificity.

> **Info:**
>
> Each index can be an object or a callback.


```jsx
<Box
  sx={[
    { mr: 2, color: 'red' },
    (theme) => ({
      '&:hover': {
        color: theme.palette.primary.main,
      },
    }),
  ]}
/>
```

## Passing the sx prop

If you want to receive the `sx` prop from a custom component and pass it down to another MUI System, we recommend this approach:


## Dynamic values

For highly dynamic CSS values, we recommend using inline CSS variables instead of passing an object with varying values to the `sx` prop on each render.
This approach avoids inserting unnecessary `style` tags into the DOM, which prevents potential performance issues when dealing with CSS properties that can hold a wide range of values that change frequently—for example, a color picker with live preview.

> **Info:**
>
> If you're having problems with your Content Security Policy while using inline styles with the `style` attribute, make sure you've enabled the [`style-src-attr` directive](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/style-src-attr).
> Visit the [Content Security Policy guide](/material-ui/guides/content-security-policy/) for configuration details.



## TypeScript usage

A frequent source of confusion with the `sx` prop is TypeScript's [type widening](https://mariusschulz.com/blog/literal-type-widening-in-typescript), which causes this example not to work as expected:

```ts
const style = {
  flexDirection: 'column',
};

export default function App() {
  return <Button sx={style}>Example</Button>;
}

// Type '{ flexDirection: string; }' is not assignable to type 'SxProps<Theme> | undefined'
// Type '{ flexDirection: string; }' is not assignable to type 'CSSSelectorObject<Theme>'
//   Property 'flexDirection' is incompatible with index signature
//     Type 'string' is not assignable to type 'SystemStyleObject<Theme>'
```

The problem is that the type of the `flexDirection` prop is inferred as `string`, which is too wide.
To fix this, you can cast the object/function passed to the `sx` prop to `const`:

```ts
const style = {
  flexDirection: 'column',
} as const;

export default function App() {
  return <Button sx={style}>Example</Button>;
}
```

Alternatively, you can pass the style object directly to the `sx` prop:

```ts
export default function App() {
  return <Button sx={{ flexDirection: 'column' }}>Example</Button>;
}
```

## Performance

To learn more about the performance tradeoffs of the `sx` prop, check out [Usage–Performance tradeoffs](/system/getting-started/usage/#performance-tradeoffs).


# Properties

# Properties

This API page lists all the custom MUI System properties, how they are linked with the theme, and which CSS properties they compute.

While this page documents the custom properties, MUI System was designed to be a superset of CSS, so all other regular CSS properties and selectors are supported too.

## Properties reference table

Note that this table only lists custom properties. All other regular CSS properties and selectors are supported too. You can check out the [legend](/system/properties/#legend) below.

| System key(s)         | CSS property/properties                                                                      | System style function                                        | Theme mapping                                                                                       |
| :-------------------- | :------------------------------------------------------------------------------------------- | :----------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| `border`              | `border`                                                                                     | [`border`](/system/borders/#border)                          | `${value}px solid`                                                                                  |
| `borderBottom`        | `border-bottom`                                                                              | [`borderBottom`](/system/borders/#border)                    | `${value}px solid`                                                                                  |
| `borderColor`         | `border-color`                                                                               | [`borderColor`](/system/borders/#border-color)               | [`theme.palette[value]`](/material-ui/customization/default-theme/?expand-path=$.palette)           |
| `borderLeft`          | `border-left`                                                                                | [`borderLeft`](/system/borders/#border)                      | `${value}px solid`                                                                                  |
| `borderRadius`        | `border-radius`                                                                              | [`borderRadius`](/system/borders/#border-radius)             | [`theme.shape.borderRadius * value`](/material-ui/customization/default-theme/?expand-path=$.shape) |
| `borderRight`         | `border-right`                                                                               | [`borderRight`](/system/borders/#border)                     | `${value}px solid`                                                                                  |
| `borderTop`           | `border-top`                                                                                 | [`borderTop`](/system/borders/#border)                       | `${value}px solid`                                                                                  |
| `boxShadow`           | `box-shadow`                                                                                 | [`boxShadow`](/system/shadows/)                              | `theme.shadows[value]`                                                                              |
| `displayPrint`        | `display`                                                                                    | [`displayPrint`](/system/display/#display-in-print)          | none                                                                                                |
| `display`             | `display`                                                                                    | [`displayRaw`](/system/display/)                             | none                                                                                                |
| `alignContent`        | `align-content`                                                                              | [`alignContent`](/system/flexbox/#align-content)             | none                                                                                                |
| `alignItems`          | `align-items`                                                                                | [`alignItems`](/system/flexbox/#align-items)                 | none                                                                                                |
| `alignSelf`           | `align-self`                                                                                 | [`alignSelf`](/system/flexbox/#align-self)                   | none                                                                                                |
| `flex`                | `flex`                                                                                       | [`flex`](/system/flexbox/)                                   | none                                                                                                |
| `flexDirection`       | `flex-direction`                                                                             | [`flexDirection`](/system/flexbox/#flex-direction)           | none                                                                                                |
| `flexGrow`            | `flex-grow`                                                                                  | [`flexGrow`](/system/flexbox/#flex-grow)                     | none                                                                                                |
| `flexShrink`          | `flex-shrink`                                                                                | [`flexShrink`](/system/flexbox/#flex-shrink)                 | none                                                                                                |
| `flexWrap`            | `flex-wrap`                                                                                  | [`flexWrap`](/system/flexbox/#flex-wrap)                     | none                                                                                                |
| `justifyContent`      | `justify-content`                                                                            | [`justifyContent`](/system/flexbox/#justify-content)         | none                                                                                                |
| `order`               | `order`                                                                                      | [`order`](/system/flexbox/#order)                            | none                                                                                                |
| `gap`                 | `gap`                                                                                        | [`gap`](/system/grid/#gap)                                   | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `columnGap`           | `column-gap`                                                                                 | [`columnGap`](/system/grid/#row-gap-column-gap)              | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `rowGap`              | `row-gap`                                                                                    | [`rowGap`](/system/grid/#row-gap-column-gap)                 | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `gridColumn`          | `grid-column`                                                                                | [`gridColumn`](/system/grid/#grid-column)                    | none                                                                                                |
| `gridRow`             | `grid-row`                                                                                   | [`gridRow`](/system/grid/#grid-row)                          | none                                                                                                |
| `gridAutoFlow`        | `grid-auto-flow`                                                                             | [`gridAutoFlow`](/system/grid/#grid-auto-flow)               | none                                                                                                |
| `gridAutoColumns`     | `grid-auto-columns`                                                                          | [`gridAutoColumns`](/system/grid/#grid-auto-columns)         | none                                                                                                |
| `gridAutoRows`        | `grid-auto-rows`                                                                             | [`gridAutoRows`](/system/grid/#grid-auto-rows)               | none                                                                                                |
| `gridTemplateColumns` | `grid-template-columns`                                                                      | [`gridTemplateColumns`](/system/grid/#grid-template-columns) | none                                                                                                |
| `gridTemplateRows`    | `grid-template-rows`                                                                         | [`gridTemplateRows`](/system/grid/#grid-template-rows)       | none                                                                                                |
| `gridTemplateAreas`   | `grid-template-areas`                                                                        | [`gridTemplateAreas`](/system/grid/#grid-template-areas)     | none                                                                                                |
| `gridArea`            | `grid-area`                                                                                  | [`gridArea`](/system/grid/#grid-area)                        | none                                                                                                |
| `bgcolor`             | `background-color`                                                                           | [`bgcolor`](/system/palette/#background-color)               | [`theme.palette[value]`](/material-ui/customization/default-theme/?expand-path=$.palette)           |
| `color`               | `color`                                                                                      | [`color`](/system/palette/#color)                            | [`theme.palette[value]`](/material-ui/customization/default-theme/?expand-path=$.palette)           |
| `bottom`              | `bottom`                                                                                     | [`bottom`](/system/positions/)                               | none                                                                                                |
| `left`                | `left`                                                                                       | [`left`](/system/positions/)                                 | none                                                                                                |
| `position`            | `position`                                                                                   | [`position`](/system/positions/)                             | none                                                                                                |
| `right`               | `right`                                                                                      | [`right`](/system/positions/)                                | none                                                                                                |
| `top`                 | `top`                                                                                        | [`top`](/system/positions/)                                  | none                                                                                                |
| `zIndex`              | `z-index`                                                                                    | [`zIndex`](/system/positions/#z-index)                       | [`theme.zIndex[value]`](/material-ui/customization/default-theme/?expand-path=$.zIndex)             |
| `height`              | `height`                                                                                     | [`height`](/system/sizing/#height)                           | none                                                                                                |
| `maxHeight`           | `max-height`                                                                                 | [`maxHeight`](/system/sizing/)                               | none                                                                                                |
| `maxWidth`            | `max-width`                                                                                  | [`maxWidth`](/system/sizing/)                                | none                                                                                                |
| `minHeight`           | `min-height`                                                                                 | [`minHeight`](/system/sizing/)                               | none                                                                                                |
| `minWidth`            | `min-width`                                                                                  | [`minWidth`](/system/sizing/)                                | none                                                                                                |
| `width`               | `width`                                                                                      | [`width`](/system/sizing/#width)                             | none                                                                                                |
| `boxSizing`           | `box-sizing`                                                                                 | [`boxSizing`](/system/sizing/)                               | none                                                                                                |
| `m`, `margin`         | `margin`                                                                                     | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `mb`, `marginBottom`  | `margin-bottom`                                                                              | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `ml`, `marginLeft`    | `margin-left`                                                                                | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `mr`, `marginRight`   | `margin-right`                                                                               | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `mt`, `marginTop`     | `margin-top`                                                                                 | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `mx`, `marginX`       | `margin-left`, `margin-right`                                                                | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `my`, `marginY`       | `margin-top`, `margin-bottom`                                                                | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `marginInline`        | `margin-inline`                                                                              | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `marginInlineStart`   | `margin-inline-start`                                                                        | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `marginInlineEnd`     | `margin-inline-end`                                                                          | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `marginBlock`         | `margin-block`                                                                               | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `marginBlockStart`    | `margin-block-start`                                                                         | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `marginBlockEnd`      | `margin-block-end`                                                                           | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `p`, `padding`        | `padding`                                                                                    | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `pb`, `paddingBottom` | `padding-bottom`                                                                             | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `pl`, `paddingLeft`   | `padding-left`                                                                               | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `pr`, `paddingRight`  | `padding-right`                                                                              | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `pt`, `paddingTop`    | `padding-top`                                                                                | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `px`, `paddingX`      | `padding-left`, `padding-right`                                                              | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `py`, `paddingY`      | `padding-top`, `padding-bottom`                                                              | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `paddingInline`       | `padding-inline`                                                                             | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `paddingInlineStart`  | `padding-inline-start`                                                                       | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `paddingInlineEnd`    | `padding-inline-end`                                                                         | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `paddingBlock`        | `padding-block`                                                                              | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `paddingBlockStart`   | `padding-block-start`                                                                        | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `paddingBlockEnd`     | `padding-block-end`                                                                          | [`spacing`](/system/spacing/)                                | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing)           |
| `typography`          | `font-family`, `font-weight`, `font-size`, `line-height`, `letter-spacing`, `text-transform` | [`typography`](/system/typography/#variant)                  | [`theme.typography[value]`](/material-ui/customization/default-theme/?expand-path=$.typography)     |
| `fontFamily`          | `font-family`                                                                                | [`fontFamily`](/system/typography/#font-family)              | [`theme.typography[value]`](/material-ui/customization/default-theme/?expand-path=$.typography)     |
| `fontSize`            | `font-size`                                                                                  | [`fontSize`](/system/typography/#font-size)                  | [`theme.typography[value]`](/material-ui/customization/default-theme/?expand-path=$.typography)     |
| `fontStyle`           | `font-style`                                                                                 | [`fontStyle`](/system/typography/#font-style)                | [`theme.typography[value]`](/material-ui/customization/default-theme/?expand-path=$.typography)     |
| `fontWeight`          | `font-weight`                                                                                | [`fontWeight`](/system/typography/#font-weight)              | [`theme.typography[value]`](/material-ui/customization/default-theme/?expand-path=$.typography)     |
| `letterSpacing`       | `letter-spacing`                                                                             | [`letterSpacing`](/system/typography/#letter-spacing)        | [`theme.typography[value]`](/material-ui/customization/default-theme/?expand-path=$.typography)     |
| `lineHeight`          | `line-height`                                                                                | [`lineHeight`](/system/typography/#line-height)              | [`theme.typography[value]`](/material-ui/customization/default-theme/?expand-path=$.typography)     |
| `textAlign`           | `text-align`                                                                                 | [`textAlign`](/system/typography/#text-alignment)            | none                                                                                                |

## Legend

Let's take one row from [the table above](#properties-reference-table), for example:

| System key(s)        | CSS property/properties | System style function         | Theme mapping                                                                             |
| :------------------- | :---------------------- | :---------------------------- | :---------------------------------------------------------------------------------------- |
| `mb`, `marginBottom` | `margin-bottom`         | [`spacing`](/system/spacing/) | [`theme.spacing(value)`](/material-ui/customization/default-theme/?expand-path=$.spacing) |

<br />

and detail each column:

- **System keys**.
  The column lists the key(s) by which you can use this property with the `sx` prop (or as a system function).

  ```jsx
  <Button sx={{ mb: 3 }}>
  // or
  <Box mb={3}>
  // or
  <Box marginBottom={3}>
  ```

- **CSS properties**.
  The column describes which CSS property will be generated when this system property is used.

  ```css
  .my-class {
    margin-bottom: Xpx;
  }
  ```

- **System style function**.
  The column lists the function which generates the properties shown in the other columns, as a reference in case you want to add this functionality to your custom components. The functions can be imported from `@mui/system`.
  You can see an example of using the style functions on the [Custom components page](/system/getting-started/custom-components/#using-standalone-system-utilities). The content links to the documentation page where this properties are described; in this example, the [spacing](/system/spacing/) page.

- **Theme mapping**.
  Lastly, the column tells you how this property is wired with the theme – with this example, whatever value you provide will be used as input to the `theme.spacing` helper.

Let's take a look at an example:

```jsx
<Button sx={{ mb: 3 }} />

// is equivalent to
<Button sx={{ marginBottom: theme => theme.spacing(3)}} />
```

As the default theme spacing is 8px, this will result in the following CSS class:

```css
.my-class {
  margin-bottom: 24px;
}
```
