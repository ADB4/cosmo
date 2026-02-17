---
title: Mui Typescript Integration
source: mui.com/material-ui
syllabus_weeks: [12]
topics: [TypeScript, module augmentation, theme typing, custom palette, custom variants, component prop typing, styled typing, createTheme typing, building extensible themes]
---



# Typescript

# TypeScript

You can add static typing to JavaScript to improve developer productivity and code quality, thanks to TypeScript.

## Minimum configuration

<!-- #target-branch-reference -->

Material UI requires a minimum version of TypeScript 4.9. Have a look at the [Vite.js with TypeScript](https://github.com/mui/material-ui/tree/master/examples/material-ui-vite-ts) example.

For types to work, it's recommended that you have at least the following options enabled in your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "lib": ["es6", "dom"],
    "noImplicitAny": true,
    "noImplicitThis": true,
    "strictNullChecks": true,
    "allowSyntheticDefaultImports": true
  }
}
```

The strict mode options are the same that are required for every types package
published in the `@types/` namespace.
Using a less strict `tsconfig.json` or omitting some of the libraries might cause errors.
To get the best type experience with the types we recommend setting `"strict": true`.

## Handling `value` and event handlers

Many components concerned with user input offer a `value` prop or event handlers
which include the current `value`. In most situations that `value` is only handled
within React which allows it be of any type, such as objects or arrays.

However, that type cannot be verified at compile time in situations where it depends on the component's children, for example `Select` or `RadioGroup`.
This means that the soundest option is to type it as `unknown` and let the developer decide how they want to narrow that type down.
We do not offer the possibility to use a generic type in those cases for [the same reasons `event.target` is not generic in React](https://github.com/DefinitelyTyped/DefinitelyTyped/issues/11508#issuecomment-256045682).

The demos include typed variants that use type casting.
It is an acceptable tradeoff because the types are all located in a single file and are very basic.
You have to decide for yourself if the same tradeoff is acceptable for you.
The library types are strict by default and loose via opt-in.

## Customization of `Theme`

Moved to [the Customizing the theme page](/material-ui/customization/theming/#custom-variables).

## Complications with the `component` prop

Because of some TypeScript limitations, using the `component` prop can be problematic if you are creating your custom component based on the Material UI's components.
For the composition of the components, you will likely need to use one of these two options:

1. Wrap the Material UI component in order to enhance it
2. Use the `styled()` utility in order to customize the styles of the component

If you are using the first option, take a look at the [composition guide](/material-ui/guides/composition/#with-typescript) for more details.

If you are using the `styled()` utility (regardless of whether it comes from `@mui/material` or `@emotion/styled`), you will need to cast the resulting component as shown below:

```tsx
import Button from '@mui/material/Button';
import { styled } from '@mui/material/styles';

const CustomButton = styled(Button)({
  // your custom styles go here
}) as typeof Button;
```


# Building Extensible Themes

# Building extensible themes

Learn how to build extensible themes with Material UI.

## Introduction

This guide describes recommendations for building a brand-specific theme with Material UI that can be easily extended and customized across multiple apps that consume it.

## Branded theme

This is the source of truth for the brand-specific theme.
It represents the brand's visual identity through colors, typography, spacing, and more.

In general, it's recommended to export tokens, components, and the branded theme from a file, as shown here:

```js title="brandedTheme.ts"
import { createTheme } from '@mui/material/styles';
import type { ThemeOptions } from '@mui/material/styles';

export const brandedTokens: ThemeOptions = {
  palette: {
    primary: {
      main: '#000000',
    },
    secondary: {
      main: 'rgb(229, 229, 234)',
    },
  },
  shape: {
    borderRadius: 4,
  },
  typography: {
    fontFamily:
      'var(--font-primary, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif)',
  },
};

export const brandedComponents: ThemeOptions['components'] = {
  MuiButton: {
    defaultProps: {
      disableElevation: true,
    },
    styleOverrides: {
      root: {
        minWidth: 'unset',
        textTransform: 'capitalize',
        '&:hover': {
          textDecoration: 'underline',
        },
      },
    },
  },
};

const brandedTheme = createTheme({
  ...brandedTokens,
  components: brandedComponents,
});

export default brandedTheme;
```

For a more optimized approach, you can split the branded components into multiple files.
This way, consumers of the theme can choose to import only what they need at the application level.

```js title="brandedButtons.ts"
import type { ThemeOptions } from "@mui/material/styles";

export const buttonTheme: ThemeOptions["components"] = {
  MuiButtonBase: {},
  MuiButton: {},
  MuiIconButton: {},
};
```

```js title="brandedTheme.ts"
import { buttonTheme } from './brandedButtons';
// import other branded components as needed

export const brandedTokens: ThemeOptions = {}

export default createTheme({
  ...brandedTokens,
  components: {
    ...buttonTheme,
    // other branded components
  },
});
```

## Application theme

Consumers of the branded theme may choose to use it directly in their applications, or extend it to better suit their specific use cases.
Using the branded button as an example, a consumer could customize its hover styles as shown below:

```js title="appTheme.ts"
import { createTheme } from '@mui/material/styles';
import { brandedTokens, brandedComponents } from './brandedTheme'; // or from an npm package.

const appTheme = createTheme({
  ...brandedTokens,
  palette: {
    ...brandedTokens.palette,
    primary: {
      main: '#1976d2',
    },
  },
  components: {
    ...brandedComponents,
    MuiButton: {
      styleOverrides: {
        root: [
          // Use array syntax to preserve the branded theme styles.
          brandedComponents?.MuiButton?.styleOverrides?.root,
          {
            '&:hover': {
              transform: 'translateY(-2px)',
            },
          },
        ],
      },
    },
  },
});
```

### Merging branded theme

When merging the branded theme with the application theme, it's recommended to use the object spread syntax for tokens like palette, typography, and shape.

For components, use the array syntax to ensure that the [variants](/material-ui/customization/theme-components/#variants), states, and pseudo-class styles from the branded theme are preserved.

> **Warning:**
>
> We don't recommend JavaScript functions or any utilities to do a deep merge between the branded and the application theme.
> 
> Doing so will introduce performance overhead on the first render of the application. The impact depends on the size of the themes.


## Full example

