---
title: Mui Theme Component Overrides
source: mui.com/material-ui
syllabus_weeks: [10]
topics: [theme styleOverrides, defaultProps, variants, themed components, slots, slotProps, ownerState, component structure, specificity, CSS layers]
---



# Theme Components

# Themed components

You can customize a component's styles, default props, and more by using its component key inside the theme.

The `components` key in the theme helps to achieve styling consistency across your application.
However, the theme isn't tree-shakable, prefer creating new components for heavy customizations.

## Theme default props

Every Material UI component has default values for each of its props.
To change these default values, use the `defaultProps` key exposed in the theme's `components` key:

```js
const theme = createTheme({
  components: {
    // Name of the component
    MuiButtonBase: {
      defaultProps: {
        // The props to change the default for.
        disableRipple: true, // No more ripple, on the whole application 💣!
      },
    },
  },
});
```


If you're using TypeScript and [lab components](/material-ui/about-the-lab/), check [this article to learn how to override their styles](/material-ui/about-the-lab/#typescript).

## Theme style overrides

The theme's `styleOverrides` key makes it possible to change the default styles of any Material UI component.

`styleOverrides` requires a slot name as a key (use `root` to target the outer-most element) and an object with CSS properties as a value.
Nested CSS selectors are also supported as values.

```js
const theme = createTheme({
  components: {
    // Name of the component
    MuiButton: {
      styleOverrides: {
        // Name of the slot
        root: {
          // Some CSS
          fontSize: '1rem',
        },
      },
    },
  },
});
```


### Variants

Most components include design-related props that affect their appearance.
For example, the Card component supports a `variant` prop where you can pick `outlined` as a value that adds a border.

If you want to override styles based on a specific prop, you can use the `variants` key in the particular slot that contains `props` and `style` keys. When the component's `props` matches, the `style` will be applied.

Override definitions are specified as an array.
Also, ensure that any styles that should take precedence are listed last.

#### Overriding styles based on existing props

The example below demonstrates the increase of the border thickness of the `outlined` Card:

```js
const theme = createTheme({
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          variants: [
            {
              props: { variant: 'outlined' },
              style: {
                borderWidth: '3px',
              },
            },
          ],
        },
      },
    },
  },
});
```

#### Adding styles based on new values

The example below demonstrates the addition of a new variant `dashed` to the Button component:

```js
const theme = createTheme({
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          variants: [
            {
              // `dashed` is an example value, it can be any name.
              props: { variant: 'dashed' },
              style: {
                textTransform: 'none',
                border: `2px dashed ${blue[500]}`,
              },
            },
          ],
        },
      },
    },
  },
});
```

#### Overriding styles based on existing and new props

The example below demonstrates the override of styles when the Button's variant is `dashed` (a new variant) and color is `secondary` (an existing color):

```js
const theme = createTheme({
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          variants: [
            {
              props: { variant: 'dashed', color: 'secondary' },
              style: {
                border: `4px dashed ${red[500]}`,
              },
            },
          ],
        },
      },
    },
  },
});
```

If you're using TypeScript, you'll need to specify your new variants/colors, using [module augmentation](https://www.typescriptlang.org/docs/handbook/declaration-merging.html#module-augmentation).

<!-- Tested with packages/mui-material/test/typescript/augmentation/themeComponents.spec.ts -->

```tsx
declare module '@mui/material/Button' {
  interface ButtonPropsVariantOverrides {
    dashed: true;
  }
}
```


The variant `props` can also be defined as a callback, allowing you to apply styles based on conditions. This is useful for styling when a property does not have a specific value.

```js
const theme = createTheme({
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          variants: [
            {
              props: (props) =>
                props.variant === 'dashed' && props.color !== 'secondary',
              style: {
                textTransform: 'none',
                border: `2px dashed ${blue[500]}`,
              },
            },
          ],
        },
      },
    },
  },
});
```

### Slot ownerState callback (deprecated)

Using callback to access slot's `ownerState` has been deprecated, use [variants](#variants) instead.

```diff
 const theme = createTheme({
   components: {
     MuiButton: {
       styleOverrides: {
-        root: ({ ownerState, theme }) => ({ ... }),
+        root: {
+          variants: [...],
         },
       },
     },
   },
 });
```

### The `sx` syntax (experimental)

The `sx` prop acts as a shortcut for defining custom styles that access the theme object.
This prop lets you write inline styles using a superset of CSS.
Learn more about [the concept behind the `sx` prop](/system/getting-started/the-sx-prop/) and [how `sx` differs from the `styled` utility](/system/styled/#difference-with-the-sx-prop).

You can use the `sx` prop inside the `styleOverrides` key to modify styles within the theme using shorthand CSS notation.
This is especially handy if you're already using the `sx` prop with your components because you can use the same syntax in your theme and quickly transfer styles between the two.

> **Info:**
>
> The `sx` prop is a stable feature for customizing components since Material UI v5, but it is still considered _experimental_ when used directly inside the theme object.



```tsx
const finalTheme = createTheme({
  components: {
    MuiChip: {
      styleOverrides: {
        root: ({ theme }) =>
          theme.unstable_sx({
            px: 1,
            py: 0.25,
            borderRadius: 1,
          }),
        label: {
          padding: 'initial',
        },
        icon: ({ theme }) =>
          theme.unstable_sx({
            mr: 0.5,
            ml: '-2px',
          }),
      },
    },
  },
});
```

### Specificity

If you use the theming approach to customize the components, you'll still be able to override them using the `sx` prop as it has a higher CSS specificity, even if you're using the experimental `sx` syntax within the theme.

## Theme variables

Another way to override the look of all component instances is to adjust the [theme configuration variables](/material-ui/customization/theming/#theme-configuration-variables).

```js
const theme = createTheme({
  typography: {
    button: {
      fontSize: '1rem',
    },
  },
});
```



# How To Customize

---
productId: material-ui
components: GlobalStyles
---

# How to customize

Learn how to customize Material UI components by taking advantage of different strategies for specific use cases.

Material UI provides several different ways to customize a component's styles. Your specific context will determine which one is ideal. From narrowest to broadest use case, here are the options:

1. [One-off customization](#1-one-off-customization)
1. [Reusable component](#2-reusable-component)
1. [Global theme overrides](#3-global-theme-overrides)
1. [Global CSS override](#4-global-css-override)

## 1. One-off customization

To change the styles of _one single instance_ of a component, you can use one of the following options:

### The `sx` prop

The [`sx` prop](/system/getting-started/the-sx-prop/) is the best option for adding style overrides to a single instance of a component in most cases.
It can be used with all Material UI components.


### Overriding nested component styles

To customize a specific part of a component, you can use the class name provided by Material UI inside the `sx` prop. As an example, let's say you want to change the `Slider` component's thumb from a circle to a square.

First, use your browser's dev tools to identify the class for the component slot you want to override.

The styles injected into the DOM by Material UI rely on class names that all [follow a standard pattern](https://v6.mui.com/system/styles/advanced/#class-names):
`[hash]-Mui[Component name]-[name of the slot]`.

In this case, the styles are applied with `.css-ae2u5c-MuiSlider-thumb` but you only really need to target the `.MuiSlider-thumb`, where `Slider` is the component and `thumb` is the slot. Use this class name to write a CSS selector within the `sx` prop (`& .MuiSlider-thumb`), and add your overrides.

<img src="/static/images/customization/dev-tools.png" alt="dev-tools" style="margin-bottom: 16px;" width="2400" height="800" />


> **Warning:**
>
> These class names can't be used as CSS selectors because they are unstable.


### Overriding styles with class names

If you want to override a component's styles using custom classes, you can use the `className` prop, available on each component.
To override the styles of a specific part of the component, use the global classes provided by Material UI, as described in the previous section **"Overriding nested component styles"** under the [`sx` prop section](#the-sx-prop).

Visit the [Style library interoperability](/material-ui/integrations/interoperability/) guide to find examples of this approach using different styling libraries.

### State classes

States like _hover_, _focus_, _disabled_ and _selected_, are styled with a higher CSS specificity. To customize them, you'll need to **increase specificity**.

Here is an example with the _disabled_ state and the `Button` component using a pseudo-class (`:disabled`):

```css
.Button {
  color: black;
}

/* Increase the specificity */
.Button:disabled {
  color: white;
}
```

```jsx
<Button disabled className="Button">
```

You can't always use a CSS pseudo-class, as the state doesn't exist in the web specification.
Let's take the `MenuItem` component and its _selected_ state as an example.
In this situation, you can use Material UI's **state classes**, which act just like CSS pseudo-classes.
Target the `.Mui-selected` global class name to customize the special state of the `MenuItem` component:

```css
.MenuItem {
  color: black;
}

/* Increase the specificity */
.MenuItem.Mui-selected {
  color: blue;
}
```

```jsx
<MenuItem selected className="MenuItem">
```

If you'd like to learn more about this topic, we recommend checking out [the MDN Web Docs on CSS Specificity](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity).

#### Why do I need to increase specificity to override one component state?

CSS pseudo-classes have a high level of specificity.
For consistency with native elements, Material UI's state classes have the same level of specificity as CSS pseudo-classes, making it possible to target an individual component's state.

#### What custom state classes are available in Material UI?

You can rely on the following [global class names](https://v6.mui.com/system/styles/advanced/#class-names) generated by Material UI:

| State         | Global class name   |
| :------------ | :------------------ |
| active        | `.Mui-active`       |
| checked       | `.Mui-checked`      |
| completed     | `.Mui-completed`    |
| disabled      | `.Mui-disabled`     |
| error         | `.Mui-error`        |
| expanded      | `.Mui-expanded`     |
| focus visible | `.Mui-focusVisible` |
| focused       | `.Mui-focused`      |
| readOnly      | `.Mui-readOnly`     |
| required      | `.Mui-required`     |
| selected      | `.Mui-selected`     |

> **Error:**
>
> Never apply styles directly to state class names. This will impact all components with unclear side-effects. Always target a state class together with a component.


```css
/* ❌ NOT OK */
.Mui-error {
  color: red;
}

/* ✅ OK */
.MuiOutlinedInput-root.Mui-error {
  color: red;
}
```

## 2. Reusable component

To reuse the same overrides in different locations across your application, create a reusable component using the [`styled()`](/system/styled/) utility:


### Dynamic overrides

The `styled()` utility lets you add dynamic styles based on a component's props.
You can do this with **dynamic CSS** or **CSS variables**.

#### Dynamic CSS

> **Warning:**
>
> If you are using TypeScript, you will need to update the prop's types of the new component.



```tsx
import * as React from 'react';
import { styled } from '@mui/material/styles';
import Slider, { SliderProps } from '@mui/material/Slider';

interface StyledSliderProps extends SliderProps {
  success?: boolean;
}

const StyledSlider = styled(Slider, {
  shouldForwardProp: (prop) => prop !== 'success',
})<StyledSliderProps>(({ success, theme }) => ({
  ...(success &&
    {
      // the overrides added when the new prop is used
    }),
}));
```

#### CSS variables


## 3. Global theme overrides

Material UI provides theme tools for managing style consistency between all components across your user interface.
Visit the [Component theming customization](/material-ui/customization/theme-components/) page for more details.

## 4. Global CSS override

To add global baseline styles for some of the HTML elements, use the `GlobalStyles` component.
Here is an example of how you can override styles for the `h1` elements:


The `styles` prop in the `GlobalStyles` component supports a callback in case you need to access the theme.


If you are already using the [CssBaseline](/material-ui/react-css-baseline/) component for setting baseline styles, you can also add these global styles as overrides for this component. Here is how you can achieve the same by using this approach.


The `styleOverrides` key in the `MuiCssBaseline` component slot also supports callback from which you can access the theme. Here is how you can achieve the same by using this approach.


> **Success:**
>
> It is a good practice to hoist the `<GlobalStyles />` to a static constant, to avoid rerendering. This will ensure that the `<style>` tag generated would not recalculate on each render.


```diff
 import * as React from 'react';
 import GlobalStyles from '@mui/material/GlobalStyles';

+const inputGlobalStyles = <GlobalStyles styles={...} />;

 function Input(props) {
   return (
     <React.Fragment>
-      <GlobalStyles styles={...} />
+      {inputGlobalStyles}
       <input {...props} />
     </React.Fragment>
   )
 }
```


# Overriding Component Structure

# Overriding component structure

Learn how to override the default DOM structure of Material UI components.

Material UI components are designed to suit the widest possible range of use cases, but you may occasionally need to change how a component's structure is rendered in the DOM.

To understand how to do this, it helps to know a bit about how the API design has evolved over time, and to have an accurate mental model of the components themselves.

## Context

Prior to Material UI v6, it was not possible to override the structure of most components in the library.
Some components had `*Props` props that allowed you to pass props to a specific slot, but this pattern was not applied consistently.

In v6, those props were deprecated in favor of the `slots` and `slotProps` props, which allow for more granular control over the structure of a component and make the API more consistent across the library.

## The mental model

A component's structure is determined by the elements that fill that component's **slots**.
Slots are most commonly filled by HTML tags, but may also be filled by React components.

All components contain a root slot that defines their primary node in the DOM tree; more complex components also contain additional interior slots named after the elements they represent.

> **Info:**
>
> To see the available slots for a component, refer to the slots sections of the respective component API documentation.


All _non-utility_ Material UI components accept two props for overriding their rendered HTML structure:

- `component`—to override the root slot
- `slots`—to replace any interior slots (when present) as well as the root

Additionally, you can pass custom props to interior slots using `slotProps`.

## The root slot

The root slot represents the component's outermost element. It is filled by a styled component with an appropriate HTML element.

For example, the [Button's](/material-ui/react-button/) root slot is a `<button>` element.
This component _only_ has a root slot; more complex components may have additional [interior slots](#interior-slots).

### The component prop

Use the `component` prop to override a component's root slot.
The demo below shows how to replace the Button's `<button>` tag with a `<a>` to create a link button:


> **Info:**
>
> The `href`, `target`, and `rel` props are specific to `<a>` tags.
> When using the `component` prop, be sure to add the appropriate attributes that correspond to the element you're inserting.


## Interior slots

Complex components are composed of one or more interior slots in addition to the root.
These slots are often (but not necessarily) nested within the root.

For example, the [Autocomplete](/material-ui/react-autocomplete/) is composed of a root `<div>` that houses several interior slots named for the elements they represent: input, startDecorator, endDecorator, clearIndicator, popupIndicator, and more.

### The slots prop

Use the `slots` prop to replace a component's interior slots.
The example below shows how to replace the popper slot in the [Autocomplete](/material-ui/react-autocomplete/) component to remove the popup functionality:


### The slotProps prop

The `slotProps` prop is an object that contains the props for all slots within a component.
You can use it to define additional custom props to pass to a component's interior slots.

For example, the code snippet below shows how to add a custom `data-testid` to the popper slot of the [Autocomplete](/material-ui/react-autocomplete/) component:

```jsx
<Autocomplete slotProps={{ popper: { 'data-testid': 'my-popper' } }} />
```

All additional props placed on the primary component are also propagated into the root slot (just as if they were placed in `slotProps.root`).
These two examples are equivalent:

```jsx
<Autocomplete id="badge1">
```

```jsx
<Autocomplete slotProps={{ root: { id: 'badge1' } }}>
```

> **Warning:**
>
> If both `slotProps.root` and additional props have the same keys but different values, the `slotProps.root` props will take precedence.
> This does not apply to classes or the `style` prop—they will be merged instead.


### Type safety

The `slotProps` prop is not dynamically typed based on the custom `slots` prop, so if the custom slot has a different type than the default slot, you have to cast the type to avoid TypeScript errors and use `satisfies` (available in TypeScript 4.9) to ensure type safety for the custom slot.

The example below shows how to customize the `img` slot of the [Avatar](/material-ui/react-avatar/) component using [Next.js Image](https://nextjs.org/docs/app/api-reference/components/image) component:

```tsx
import Image, { ImageProps } from 'next/image';
import Avatar, { AvatarProps } from '@mui/material/Avatar';

<Avatar
  slots={{
    img: Image,
  }}
  slotProps={
    {
      img: {
        src: 'https://example.com/image.jpg',
        alt: 'Image',
        width: 40,
        height: 40,
        blurDataURL: 'data:image/png;base64',
      } satisfies ImageProps,
    } as AvatarProps['slotProps']
  }
/>;
```

## Best practices

Use the `component` or `slotProps.{slot}.component` prop when you need to override the element while preserving the styles of the slot.

Use the `slots` prop when you need to replace the slot's styles and functionality with your custom component.

Overriding with `component` lets you apply the attributes of that element directly to the root.
For instance, if you override the Button's root with an `<li>` tag, you can add the `<li>` attribute `value` directly to the component.
If you did the same with `slots.root`, you would need to place this attribute on the `slotProps.root` object in order to avoid a TypeScript error.

Be mindful of your rendered DOM structure when overriding the slots of more complex components.
You can easily break the rules of semantic and accessible HTML if you deviate too far from the default structure—for instance, by unintentionally nesting block-level elements inside of inline elements.


# Creating Themed Components

# Creating themed components

Learn how to create fully custom components that accept your app's theme.

## Introduction

Material UI provides a powerful theming feature that lets you add your own components to the theme and treat them as if they're built-in components.

If you are building a component library on top of Material UI, you can follow the step-by-step guide below to create a custom component that is themeable across multiple projects.

Alternatively, you can use the provided [template](#template) as a starting point for your component.

> **Info:**
>
> You don't need to connect your component to the theme if you are only using it in a single project.


## Step-by-step guide

This guide will walk you through how to build this statistics component, which accepts the app's theme as though it were a built-in Material UI component:


### 1. Create the component slots

Slots let you customize each individual element of the component by targeting its respective name in the [theme's styleOverrides](/material-ui/customization/theme-components/#theme-style-overrides) and [theme's variants](/material-ui/customization/theme-components/#variants).

This statistics component is composed of three slots:

- `root`: the container of the component
- `value`: the number of the statistics
- `unit`: the unit or description of the statistics

> **Success:**
>
> Though you can give these slots any names you prefer, we recommend using `root` for the outermost container element for consistency with the rest of the library.



Use the `styled` API with `name` and `slot` parameters to create the slots, as shown below:

```js
import * as React from 'react';
import { styled } from '@mui/material/styles';

const StatRoot = styled('div', {
  name: 'MuiStat', // The component name
  slot: 'root', // The slot name
})(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(0.5),
  padding: theme.spacing(3, 4),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
  letterSpacing: '-0.025em',
  fontWeight: 600,
  ...theme.applyStyles('dark', {
    backgroundColor: 'inherit',
  }),
}));

const StatValue = styled('div', {
  name: 'MuiStat',
  slot: 'value',
})(({ theme }) => ({
  ...theme.typography.h3,
}));

const StatUnit = styled('div', {
  name: 'MuiStat',
  slot: 'unit',
})(({ theme }) => ({
  ...theme.typography.body2,
  color: theme.palette.text.secondary,
}));
```

### 2. Create the component

Assemble the component using the slots created in the previous step:

```js
// /path/to/Stat.js
import * as React from 'react';

const StatRoot = styled('div', {
  name: 'MuiStat',
  slot: 'root',
})(…);

const StatValue = styled('div', {
  name: 'MuiStat',
  slot: 'value',
})(…);

const StatUnit = styled('div', {
  name: 'MuiStat',
  slot: 'unit',
})(…);

const Stat = React.forwardRef(function Stat(props, ref) {
  const { value, unit, ...other } = props;

  return (
    <StatRoot ref={ref} {...other}>
      <StatValue>{value}</StatValue>
      <StatUnit>{unit}</StatUnit>
    </StatRoot>
  );
});

export default Stat;
```

At this point, you'll be able to apply the theme to the `Stat` component like this:

```js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  components: {
    // the component name defined in the `name` parameter
    // of the `styled` API
    MuiStat: {
      styleOverrides: {
        // the slot name defined in the `slot` and `overridesResolver` parameters
        // of the `styled` API
        root: {
          backgroundColor: '#121212',
        },
        value: {
          color: '#fff',
        },
        unit: {
          color: '#888',
        },
      },
    },
  },
});
```

### 3. Style the slot with ownerState

When you need to style the slot-based props or internal state, wrap them in the `ownerState` object and pass it to each slot as a prop.
The `ownerState` is a special name that will not spread to the DOM via the `styled` API.

Add a `variant` prop to the `Stat` component and use it to style the `root` slot, as shown below:

```diff
  const Stat = React.forwardRef(function Stat(props, ref) {
+   const { value, unit, variant, ...other } = props;
+
+   const ownerState = { ...props, variant };

    return (
-      <StatRoot ref={ref} {...other}>
-        <StatValue>{value}</StatValue>
-        <StatUnit>{unit}</StatUnit>
-      </StatRoot>
+      <StatRoot ref={ref} ownerState={ownerState} {...other}>
+        <StatValue ownerState={ownerState}>{value}</StatValue>
+        <StatUnit ownerState={ownerState}>{unit}</StatUnit>
+      </StatRoot>
    );
  });
```

Then you can read `ownerState` in the slot to style it based on the `variant` prop.

```diff
  const StatRoot = styled('div', {
    name: 'MuiStat',
    slot: 'root',
-  })(({ theme }) => ({
+  })(({ theme, ownerState }) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(0.5),
    padding: theme.spacing(3, 4),
    backgroundColor: theme.palette.background.paper,
    borderRadius: theme.shape.borderRadius,
    boxShadow: theme.shadows[2],
    letterSpacing: '-0.025em',
    fontWeight: 600,
    ...theme.applyStyles('dark', {
      backgroundColor: 'inherit',
    }),
+   ...ownerState.variant === 'outlined' && {
+    border: `2px solid ${theme.palette.divider}`,
+   },
  }));
```

### 4. Support theme default props

To customize your component's default props for different projects, you need to use the `useThemeProps` API.

```diff
+ import { useThemeProps } from '@mui/material/styles';

- const Stat = React.forwardRef(function Stat(props, ref) {
+ const Stat = React.forwardRef(function Stat(inProps, ref) {
+   const props = useThemeProps({ props: inProps, name: 'MuiStat' });
    const { value, unit, ...other } = props;

    return (
      <StatRoot ref={ref} {...other}>
        <StatValue>{value}</StatValue>
        <StatUnit>{unit}</StatUnit>
      </StatRoot>
    );
  });
```

Then you can customize the default props of your component like this:

```js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  components: {
    MuiStat: {
      defaultProps: {
        variant: 'outlined',
      },
    },
  },
});
```

## TypeScript

If you use TypeScript, you must create interfaces for the component props and ownerState:

```js
interface StatProps {
  value: number | string;
  unit: string;
  variant?: 'outlined';
}

interface StatOwnerState extends StatProps {
  // …key value pairs for the internal state that you want to style the slot
  // but don't want to expose to the users
}
```

Then you can use them in the component and slots.

```js
const StatRoot = styled('div', {
  name: 'MuiStat',
  slot: 'root',
})<{ ownerState: StatOwnerState }>(({ theme, ownerState }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(0.5),
  padding: theme.spacing(3, 4),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
  letterSpacing: '-0.025em',
  fontWeight: 600,
  ...theme.applyStyles('dark', {
    backgroundColor: 'inherit',
  }),
  // typed-safe access to the `variant` prop
  ...(ownerState.variant === 'outlined' && {
    border: `2px solid ${theme.palette.divider}`,
    boxShadow: 'none',
  }),
}));

// …do the same for other slots

const Stat = React.forwardRef<HTMLDivElement, StatProps>(function Stat(inProps, ref) {
  const props = useThemeProps({ props: inProps, name: 'MuiStat' });
  const { value, unit, variant, ...other } = props;

  const ownerState = { ...props, variant };

  return (
    <StatRoot ref={ref} ownerState={ownerState} {...other}>
      <StatValue ownerState={ownerState}>{value}</StatValue>
      <StatUnit ownerState={ownerState}>{unit}</StatUnit>
    </StatRoot>
  );
});
```

Finally, add the Stat component to the theme types.

```ts
import {
  ComponentsOverrides,
  ComponentsVariants,
  Theme as MuiTheme,
} from '@mui/material/styles';
import { StatProps } from 'path/to/Stat';

type Theme = Omit<MuiTheme, 'components'>;

declare module '@mui/material/styles' {
  interface ComponentNameToClassKey {
    MuiStat: 'root' | 'value' | 'unit';
  }

  interface ComponentsPropsList {
    MuiStat: Partial<StatProps>;
  }

  interface Components {
    MuiStat?: {
      defaultProps?: ComponentsPropsList['MuiStat'];
      styleOverrides?: ComponentsOverrides<Theme>['MuiStat'];
      variants?: ComponentsVariants['MuiStat'];
    };
  }
}
```

---

## Template

This template is the final product of the step-by-step guide above, demonstrating how to build a custom component that can be styled with the theme as if it was a built-in component.



# Css Layers

# CSS Layers

Learn how to generate Material UI styles with cascade layers.

## What are cascade layers?

Cascade layers are an advanced CSS feature that make it possible to control the order in which styles are applied to elements.
If you're not familiar with cascade layers, visit the [MDN documentation](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Cascade_layers) for a detailed overview.

Benefits of using cascade layers include:

- **Improved specificity**: Cascade layers let you control the order of the styles, which can help avoid specificity conflicts. For example, you can theme a component without hitting the default specificity of the styles.
- **Better integration with CSS frameworks**: With cascade layers, you can use Tailwind CSS v4 utility classes to override Material UI styles without the need for the `!important` directive.
- **Better debuggability**: Cascade layers appear in the browser's dev tools, making it easier to see which styles are applied and in what order.

## Implementing a single cascade layer

This method creates a single layer, namely `@layer mui`, for all Material UI components and global styles.
This is suitable for integrating with other styling solutions, such as Tailwind CSS v4, that use the `@layer` directive.

### Next.js App Router

Start by configuring Material UI with Next.js in the [App Router integration guide](/material-ui/integrations/nextjs/#app-router).
Then follow these steps:

1. Enable the [CSS layer feature](/material-ui/integrations/nextjs/#using-other-styling-solutions) in the root layout:

```tsx title="src/app/layout.tsx"
import { AppRouterCacheProvider } from '@mui/material-nextjs/v15-appRouter';

export default function RootLayout() {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <AppRouterCacheProvider options={{ enableCssLayer: true }}>
          {/* Your app */}
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
```

2. Configure the layer order at the top of a CSS file to work with Tailwind CSS v4:

```css title="src/app/globals.css"
@layer theme, base, mui, components, utilities;
```

### Next.js Pages Router

Start by configuring Material UI with Next.js in the [Pages Router integration guide](/material-ui/integrations/nextjs/#pages-router).
Then follow these steps:

1. Enable the [CSS layer feature](/material-ui/integrations/nextjs/#configuration-2) in a custom `_document`:

```tsx title="pages/_document.tsx"
import {
  createCache,
  documentGetInitialProps,
} from '@mui/material-nextjs/v15-pagesRouter';

// ...

MyDocument.getInitialProps = async (ctx: DocumentContext) => {
  const finalProps = await documentGetInitialProps(ctx, {
    emotionCache: createCache({ enableCssLayer: true }),
  });
  return finalProps;
};
```

2. Configure the layer order with the `GlobalStyles` component to work with Tailwind CSS v4—it must be the first child of the `AppCacheProvider`:

```tsx title="pages/_app.tsx"
import { AppCacheProvider } from '@mui/material-nextjs/v15-pagesRouter';
import GlobalStyles from '@mui/material/GlobalStyles';

export default function MyApp(props: AppProps) {
  const { Component, pageProps } = props;
  return (
    <AppCacheProvider {...props}>
      <GlobalStyles styles="@layer theme, base, mui, components, utilities;" />
      <Component {...pageProps} />
    </AppCacheProvider>
  );
}
```

### Vite or any other SPA

Make the following changes in `src/main.tsx`:

1. Pass the `enableCssLayer` prop to the `StyledEngineProvider` component.
2. Configure the layer order with the `GlobalStyles` component to work with Tailwind CSS v4.

```tsx title="main.tsx"
import { StyledEngineProvider } from '@mui/material/styles';
import GlobalStyles from '@mui/material/GlobalStyles';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <StyledEngineProvider enableCssLayer>
      <GlobalStyles styles="@layer theme, base, mui, components, utilities;" />
      {/* Your app */}
    </StyledEngineProvider>
  </React.StrictMode>,
);
```

## Implementing multiple cascade layers

After you've set up a [single cascade layer](#implementing-a-single-cascade-layer), you can split the styles into multiple layers to better organize them within Material UI.
This makes it simpler to apply theming and override styles with the `sx` prop.

First, follow the steps from the [previous section](#implementing-a-single-cascade-layer) to enable the CSS layer feature.
Then, create a new file and export the component that wraps the `ThemeProvider` from Material UI.
Finally, pass the `modularCssLayers: true` option to the `createTheme` function:

```tsx title="src/theme.tsx"
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  modularCssLayers: true,
});

export default function AppTheme({ children }: { children: ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}
```


When this feature is enabled, Material UI generates these layers:

- `@layer mui.global`: Global styles from the `GlobalStyles` and `CssBaseline` components.
- `@layer mui.components`: Base styles for all Material UI components.
- `@layer mui.theme`: Theme styles for all Material UI components.
- `@layer mui.custom`: Custom styles for non-Material UI styled components.
- `@layer mui.sx`: Styles from the `sx` prop.

The sections below demonstrate how to set up multiple cascade layers for Material UI with common React frameworks.

### Next.js App Router

```tsx title="src/theme.tsx"
'use client';
import React from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  modularCssLayers: true,
});

export default function AppTheme({ children }: { children: React.ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}
```

```tsx title="src/app/layout.tsx"
import AppTheme from '../theme';

export default function RootLayout() {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <AppRouterCacheProvider options={{ enableCssLayer: true }}>
          <AppTheme>{/* Your app */}</AppTheme>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
```

### Next.js Pages Router

```tsx title="src/theme.tsx"
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  modularCssLayers: true,
});

export default function AppTheme({ children }: { children: ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}
```

```tsx title="pages/_app.tsx"
import AppTheme from '../src/theme';

export default function MyApp(props: AppProps) {
  const { Component, pageProps } = props;
  return (
    <AppCacheProvider {...props}>
      <AppTheme>
        <Component {...pageProps} />
      </AppTheme>
    </AppCacheProvider>
  );
}
```

```tsx title="pages/_document.tsx"
import {
  createCache,
  documentGetInitialProps,
} from '@mui/material-nextjs/v15-pagesRouter';

MyDocument.getInitialProps = async (ctx: DocumentContext) => {
  const finalProps = await documentGetInitialProps(ctx, {
    emotionCache: createCache({ enableCssLayer: true }),
  });
  return finalProps;
};
```

### Vite or any other SPA

```tsx title="src/theme.tsx"
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  modularCssLayers: true,
});

export default function AppTheme({ children }: { children: ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}
```

```tsx title="src/main.tsx"
import AppTheme from './theme';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <StyledEngineProvider enableCssLayer>
      <AppTheme>{/* Your app */}</AppTheme>
    </StyledEngineProvider>
  </React.StrictMode>,
);
```

### Usage with other styling solutions

To integrate with other styling solutions, such as Tailwind CSS v4, replace the boolean value for `modularCssLayers` with a string specifying the layer order.
Material UI will look for the `mui` identifier and generate the layers in the correct order:

```diff title="src/theme.tsx"
 const theme = createTheme({
-  modularCssLayers: true,
+  modularCssLayers: '@layer theme, base, mui, components, utilities;',
 });
```

The generated CSS will look like this:

```css
@layer theme, base, mui.global, mui.components, mui.theme, mui.custom, mui.sx, components, utilities;
```

### Caveats

If you enable `modularCssLayers` in an app that already has custom styles and theme overrides applied to it, you may observe unexpected changes to the look and feel of the UI due to the differences in specificity before and after.

For example, if you have the following [theme style overrides](/material-ui/customization/theme-components/#theme-style-overrides) for the [Accordion](/material-ui/react-accordion/) component:

```js
const theme = createTheme({
  components: {
    MuiAccordion: {
      styleOverrides: {
        root: {
          margin: 0,
        },
      },
    },
  },
});
```

By default, the margin from the theme does _not_ take precedence over the default margin styles when the accordion is expanded, because it has higher specificity than the theme styles—so this code has no effect.

After enabling the `modularCssLayers` option, the margin from the theme _does_ take precedence because the theme layer comes after the components layer in the cascade order—so the style override is applied and the accordion has no margins when expanded.

