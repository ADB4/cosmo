---
title: Mui Complex Components
source: mui.com/material-ui
syllabus_weeks: [11]
topics: [Autocomplete, combo box, free solo, Dialog, alert dialog, form dialog, full-screen dialog, Drawer, temporary, persistent, Snackbar, Stepper, linear, non-linear, Select, native select, multiple select]
---



# Autocomplete

---
productId: material-ui
title: React Autocomplete component
components: TextField, Popper, Autocomplete
githubLabel: 'scope: autocomplete'
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/combobox/
githubSource: packages/mui-material/src/Autocomplete
---

# Autocomplete

The autocomplete is a normal text input enhanced by a panel of suggested options.

The widget is useful for setting the value of a single-line textbox in one of two types of scenarios:

1. The value for the textbox must be chosen from a predefined set of allowed values, for example a location field must contain a valid location name: [combo box](#combo-box).
2. The textbox may contain any arbitrary value, but it is advantageous to suggest possible values to the user, for example a search field may suggest similar or previous searches to save the user time: [free solo](#free-solo).

It's meant to be an improved version of the "react-select" and "downshift" packages.


## Combo box

The value must be chosen from a predefined set of allowed values.


### Options structure

By default, the component accepts the following options structures:

```ts
interface AutocompleteOption {
  label: string;
}
// or
type AutocompleteOption = string;
```

for instance:

```js
const options = [
  { label: 'The Godfather', id: 1 },
  { label: 'Pulp Fiction', id: 2 },
];
// or
const options = ['The Godfather', 'Pulp Fiction'];
```

However, you can use different structures by providing a `getOptionLabel` prop.

If your options are objects, you must provide the `isOptionEqualToValue` prop to ensure correct selection and highlighting. By default, it uses strict equality to compare options with the current value.

> **Warning:**
>
> If your options have duplicate labels, you must extract a unique key with the `getOptionKey` prop.
> 
> ```tsx
> const options = [
>   { label: 'The Godfather', id: 1 },
>   { label: 'The Godfather', id: 2 },
> ];
> 
> return <Autocomplete options={options} getOptionKey={(option) => option.id} />;
> ```


### Playground

Each of the following examples demonstrates one feature of the Autocomplete component.


### Country select

Choose one of the 248 countries.


### Controlled states

The component has two states that can be controlled:

1. the "value" state with the `value`/`onChange` props combination. This state represents the value selected by the user, for instance when pressing <kbd class="key">Enter</kbd>.
2. the "input value" state with the `inputValue`/`onInputChange` props combination. This state represents the value displayed in the textbox.

These two states are isolated, and should be controlled independently.

> **Info:**
>
> - A component is **controlled** when it's managed by its parent using props.
> - A component is **uncontrolled** when it's managed by its own local state.
> 
> Learn more about controlled and uncontrolled components in the [React documentation](https://react.dev/learn/sharing-state-between-components#controlled-and-uncontrolled-components).



> **Warning:**
>
> If you control the `value`, make sure it's referentially stable between renders.
> In other words, the reference to the value shouldn't change if the value itself doesn't change.
> 
> ```tsx
> // ⚠️ BAD
> return <Autocomplete multiple value={allValues.filter((v) => v.selected)} />;
> 
> // 👍 GOOD
> const selectedValues = React.useMemo(
>   () => allValues.filter((v) => v.selected),
>   [allValues],
> );
> return <Autocomplete multiple value={selectedValues} />;
> ```
> 
> In the first example, `allValues.filter` is called and returns **a new array** every render.
> The fix includes memoizing the value, so it changes only when needed.


## Free solo

Set `freeSolo` to true so the textbox can contain any arbitrary value.

### Search input

The prop is designed to cover the primary use case of a **search input** with suggestions, for example Google search or react-autowhatever.


> **Warning:**
>
> Be careful when using the free solo mode with non-string options, as it may cause type mismatch.
> 
> The value created by typing into the textbox is always a string, regardless of the type of the options.


### Creatable

If you intend to use this mode for a [combo box](#combo-box) like experience (an enhanced version of a select element) we recommend setting:

- `selectOnFocus` to help the user clear the selected value.
- `clearOnBlur` to help the user enter a new value.
- `handleHomeEndKeys` to move focus inside the popup with the <kbd class="key">Home</kbd> and <kbd class="key">End</kbd> keys.
- A last option, for instance: `Add "YOUR SEARCH"`.


You could also display a dialog when the user wants to add a new value.


## Grouped

You can group the options with the `groupBy` prop.
If you do so, make sure that the options are also sorted with the same dimension that they are grouped by,
otherwise, you will notice duplicate headers.


To control how the groups are rendered, provide a custom `renderGroup` prop.
This is a function that accepts an object with two fields:

- `group`—a string representing a group name
- `children`—a collection of list items that belong to the group

The following demo shows how to use this prop to define custom markup and override the styles of the default groups:


## Disabled options


## `useAutocomplete`

For advanced customization use cases, a headless `useAutocomplete()` hook is exposed.
It accepts almost the same options as the Autocomplete component minus all the props
related to the rendering of JSX.
The Autocomplete component is built on this hook.

```tsx
import { useAutocomplete } from '@mui/base/useAutocomplete';
```

The `useAutocomplete` hook is also reexported from @mui/material for convenience and backward compatibility.

```tsx
import useAutocomplete from '@mui/material/useAutocomplete';
```

- 📦 [4.6 kB gzipped](https://bundlephobia.com/package/@mui/material).


### Customized hook


Head to the [customization](#customization) section for an example with the `Autocomplete` component instead of the hook.

## Asynchronous requests

The component supports two different asynchronous use-cases:

- [Load on open](#load-on-open): it waits for the component to be interacted with to load the options.
- [Search as you type](#search-as-you-type): a new request is made for each keystroke.

### Load on open

It displays a progress state as long as the network request is pending.


### Search as you type

If your logic is fetching new options on each keystroke and using the current value of the textbox
to filter on the server, you may want to consider throttling requests.

Additionally, you will need to disable the built-in filtering of the `Autocomplete` component by
overriding the `filterOptions` prop:

```jsx
<Autocomplete filterOptions={(x) => x} />
```

### Google Maps place

A customized UI for Google Maps Places Autocomplete.
For this demo, we need to load the [Google Maps JavaScript](https://developers.google.com/maps/documentation/javascript/overview) and [Google Places](https://developers.google.com/maps/documentation/places/web-service/overview) API.


The demo relies on [autosuggest-highlight](https://github.com/moroshko/autosuggest-highlight), a small (1 kB) utility for highlighting text in autosuggest and autocomplete components.

> **Error:**
>
> Before you can start using the Google Maps JavaScript API and Places API, you need to get your own [API key](https://developers.google.com/maps/documentation/javascript/get-api-key).
> 
> This demo has limited quotas to make API requests. When your quota exceeds, you will see the response for "Paris".


## Single value rendering

By default (when `multiple={false}`), the selected option is displayed as plain text inside the input.
The `renderValue` prop allows you to customize how the selected value is rendered.
This can be useful for adding custom styles, displaying additional information, or formatting the value differently.

- The `getItemProps` getter provides props like `data-item-index`, `disabled`, `tabIndex` and others. These props should be spread onto the rendered component for proper accessibility.
- If using a custom component other than a Material UI Chip, destructure the `onDelete` prop as it's specific to the Material UI Chip.


## Multiple values

When `multiple={true}`, the user can select multiple values. These selected values, referred to as "items" can be customized using the `renderValue` prop.

- The `getItemProps` getter supplies essential props like `data-item-index`, `disabled`, `tabIndex` and others. Make sure to spread them on each rendered item.
- If using a custom component other than a Material UI Chip, destructure the `onDelete` prop as it's specific to the Material UI Chip.


### Fixed options

In the event that you need to lock certain tags so that they can't be removed, you can set the chips disabled.


### Selection indicators

This example demonstrates how icons are used to indicate the selection state of each item in the listbox.


### Limit tags

You can use the `limitTags` prop to limit the number of displayed options when not focused.


## Sizes

Fancy smaller inputs? Use the `size` prop.


## Customization

### Custom input

The `renderInput` prop allows you to customize the rendered input.
The first argument of this render prop contains props that you need to forward.
Pay specific attention to the `ref` and `inputProps` keys.

> **Warning:**
>
> If you're using a custom input component inside the Autocomplete, make sure that you forward the ref to the underlying DOM element.



### Globally customized options

To globally customize the Autocomplete options for all components in your app,
you can use the [theme default props](/material-ui/customization/theme-components/#theme-default-props) and set the `renderOption` property in the `defaultProps` key.
The `renderOption` property takes the `ownerState` as the fourth parameter, which includes props and internal component state.
To display the label, you can use the `getOptionLabel` prop from the `ownerState`.
This approach enables different options for each Autocomplete component while keeping the options styling consistent.


### GitHub's picker

This demo reproduces GitHub's label picker:


Head to the [Customized hook](#customized-hook) section for a customization example with the `useAutocomplete` hook instead of the component.

### Hint

The following demo shows how to add a hint feature to the Autocomplete:


## Highlights

The following demo relies on [autosuggest-highlight](https://github.com/moroshko/autosuggest-highlight), a small (1 kB) utility for highlighting text in autosuggest and autocomplete components.


## Custom filter

The component exposes a factory to create a filter method that can be provided to the `filterOptions` prop.
You can use it to change the default option filter behavior.

```js
import { createFilterOptions } from '@mui/material/Autocomplete';
```

### `createFilterOptions(config) => filterOptions`

#### Arguments

1. `config` (_object_ [optional]):

- `config.ignoreAccents` (_bool_ [optional]): Defaults to `true`. Remove diacritics.
- `config.ignoreCase` (_bool_ [optional]): Defaults to `true`. Lowercase everything.
- `config.limit` (_number_ [optional]): Default to null. Limit the number of suggested options to be shown. For example, if `config.limit` is `100`, only the first `100` matching options are shown. It can be useful if a lot of options match and virtualization wasn't set up.
- `config.matchFrom` (_'any' | 'start'_ [optional]): Defaults to `'any'`.
- `config.stringify` (_func_ [optional]): Controls how an option is converted into a string so that it can be matched against the input text fragment.
- `config.trim` (_bool_ [optional]): Defaults to `false`. Remove trailing spaces.

#### Returns

`filterOptions`: the returned filter method can be provided directly to the `filterOptions` prop of the `Autocomplete` component, or the parameter of the same name for the hook.

In the following demo, the options need to start with the query prefix:

```jsx
const filterOptions = createFilterOptions({
  matchFrom: 'start',
  stringify: (option) => option.title,
});

<Autocomplete filterOptions={filterOptions} />;
```


### Advanced

For richer filtering mechanisms, like fuzzy matching, it's recommended to look at [match-sorter](https://github.com/kentcdodds/match-sorter). For instance:

```jsx
import { matchSorter } from 'match-sorter';

const filterOptions = (options, { inputValue }) => matchSorter(options, inputValue);

<Autocomplete filterOptions={filterOptions} />;
```

## Virtualization

Search within 10,000 randomly generated options. The list is virtualized thanks to [react-window](https://github.com/bvaughn/react-window).


## Events

If you would like to prevent the default key handler behavior, you can set the event's `defaultMuiPrevented` property to `true`:

```jsx
<Autocomplete
  onKeyDown={(event) => {
    if (event.key === 'Enter') {
      // Prevent's default 'Enter' behavior.
      event.defaultMuiPrevented = true;
      // your handler code
    }
  }}
/>
```

## Limitations

### autocomplete/autofill

Browsers have heuristics to help the user fill in form inputs.
However, this can harm the UX of the component.

By default, the component disables the input **autocomplete** feature (remembering what the user has typed for a given field in a previous session) with the `autoComplete="off"` attribute.
Google Chrome does not currently support this attribute setting ([Issue 41239842](https://issues.chromium.org/issues/41239842)).
A possible workaround is to remove the `id` to have the component generate a random one.

In addition to remembering past entered values, the browser might also propose **autofill** suggestions (saved login, address, or payment details).
In the event you want the avoid autofill, you can try the following:

- Name the input without leaking any information the browser can use. For example `id="field1"` instead of `id="country"`. If you leave the id empty, the component uses a random id.
- Set `autoComplete="new-password"` (some browsers will suggest a strong password for inputs with this attribute setting):

  ```jsx
  <TextField
    {...params}
    inputProps={{
      ...params.inputProps,
      autoComplete: 'new-password',
    }}
  />
  ```

Read [the guide on MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Turning_off_form_autocompletion) for more details.

### iOS VoiceOver

VoiceOver on iOS Safari doesn't support the `aria-owns` attribute very well.
You can work around the issue with the `disablePortal` prop.

### ListboxComponent

If you provide a custom `ListboxComponent` prop, you need to make sure that the intended scroll container has the `role` attribute set to `listbox`. This ensures the correct behavior of the scroll, for example when using the keyboard to navigate.

## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/combobox/)

We encourage the usage of a label for the textbox.
The component implements the WAI-ARIA authoring practices.


# Dialogs

---
productId: material-ui
title: React Dialog component
components: Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Slide
githubLabel: 'scope: dialog'
materialDesign: https://m2.material.io/components/dialogs
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/
githubSource: packages/mui-material/src/Dialog
---

# Dialog

Dialogs inform users about a task and can contain critical information, require decisions, or involve multiple tasks.

A Dialog is a type of [modal](/material-ui/react-modal/) window that appears in front of app content to provide critical information or ask for a decision. Dialogs disable all app functionality when they appear, and remain on screen until confirmed, dismissed, or a required action has been taken.

Dialogs are purposefully interruptive, so they should be used sparingly.


## Introduction

Dialogs are implemented using a collection of related components:

- Dialog: the parent component that renders the modal.
- Dialog Title: a wrapper used for the title of a Dialog.
- Dialog Actions: an optional container for a Dialog's Buttons.
- Dialog Content: an optional container for displaying the Dialog's content.
- Dialog Content Text: a wrapper for text inside of `<DialogContent />`.
- Slide: optional [Transition](/material-ui/transitions/#slide) used to slide the Dialog in from the edge of the screen.


## Basics

```jsx
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
```

## Alerts

Alerts are urgent interruptions, requiring acknowledgement, that inform the user about a situation.

Most alerts don't need titles.
They summarize a decision in a sentence or two by either:

- Asking a question (for example "Delete this conversation?")
- Making a statement related to the action buttons

Use title bar alerts only for high-risk situations, such as the potential loss of connectivity.
Users should be able to understand the choices based on the title and button text alone.

If a title is required:

- Use a clear question or statement with an explanation in the content area, such as "Erase USB storage?".
- Avoid apologies, ambiguity, or questions, such as "Warning!" or "Are you sure?"


## Transitions

You can also swap out the transition, the next example uses `Slide`.


## Form dialogs

Form dialogs allow users to fill out form fields within a dialog.
For example, if your site prompts for potential subscribers to fill in their email address, they can fill out the email field and touch 'Submit'.


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).

The dialog has a close button added to aid usability.


## Full-screen dialogs


## Optional sizes

You can set a dialog maximum width by using the `maxWidth` enumerable in combination with the `fullWidth` boolean.
When the `fullWidth` prop is true, the dialog will adapt based on the `maxWidth` value.


## Responsive full-screen

You may make a dialog responsively full screen using [`useMediaQuery`](/material-ui/react-use-media-query/).

```jsx
import useMediaQuery from '@mui/material/useMediaQuery';

function MyComponent() {
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'));

  return <Dialog fullScreen={fullScreen} />;
}
```


## Confirmation dialogs

Confirmation dialogs require users to explicitly confirm their choice before an option is committed.
For example, users can listen to multiple ringtones but only make a final selection upon touching "OK".

Touching "Cancel" in a confirmation dialog, cancels the action, discards any changes, and closes the dialog.


## Non-modal dialog

Dialogs can also be non-modal, meaning they don't interrupt user interaction behind it.
Visit [the Nielsen Norman Group article](https://www.nngroup.com/articles/modal-nonmodal-dialog/) for more in-depth guidance about modal vs. non-modal dialog usage.

The demo below shows a persistent cookie banner, a common non-modal dialog use case.


## Draggable dialog

You can create a draggable dialog by using [react-draggable](https://github.com/react-grid-layout/react-draggable).
To do so, you can pass the imported `Draggable` component as the `PaperComponent` of the `Dialog` component.
This will make the entire dialog draggable.


## Scrolling long content

When dialogs become too long for the user's viewport or device, they scroll.

- `scroll=paper` the content of the dialog scrolls within the paper element.
- `scroll=body` the content of the dialog scrolls within the body element.

Try the demo below to see what we mean:


## Performance

Follow the [Modal performance section](/material-ui/react-modal/#performance).

## Limitations

Follow the [Modal limitations section](/material-ui/react-modal/#limitations).

## Supplementary projects

For more advanced use cases you might be able to take advantage of:

### material-ui-confirm

![stars](https://img.shields.io/github/stars/jonatanklosko/material-ui-confirm?style=social&label=Star)
![npm downloads](https://img.shields.io/npm/dm/material-ui-confirm.svg)

The package [`material-ui-confirm`](https://github.com/jonatanklosko/material-ui-confirm/) provides dialogs for confirming user actions without writing boilerplate code.

## Accessibility

Follow the [Modal accessibility section](/material-ui/react-modal/#accessibility).


# Drawers

---
productId: material-ui
title: React Drawer component
components: Drawer, SwipeableDrawer
githubLabel: 'scope: drawer'
materialDesign: https://m2.material.io/components/navigation-drawer
githubSource: packages/mui-material/src/Drawer
---

# Drawer

The navigation drawers (or "sidebars") provide ergonomic access to destinations in a site or app functionality such as switching accounts.

A navigation drawer can either be permanently on-screen or controlled by a navigation menu icon.

[Side sheets](https://m2.material.io/components/sheets-side) are supplementary surfaces primarily used on tablet and desktop.


## Temporary drawer

Temporary navigation drawers can toggle open or closed. Closed by default, the drawer opens temporarily above all other content until a section is selected.

The Drawer can be cancelled by clicking the overlay or pressing the Esc key.
It closes when an item is selected, handled by controlling the `open` prop.


### Anchor

Use the `anchor` prop to specify which side of the screen the Drawer should originate from.

The default value is `left`.


### Swipeable

You can make the drawer swipeable with the `SwipeableDrawer` component.

This component comes with a 2 kB gzipped payload overhead.
Some low-end mobile devices won't be able to follow the fingers at 60 FPS.
You can use the `disableBackdropTransition` prop to help.


The following properties are used in this documentation website for optimal usability of the component:

- iOS is hosted on high-end devices.
  The backdrop transition can be enabled without dropping frames.
  The performance will be good enough.
- iOS has a "swipe to go back" feature that interferes
  with the discovery feature, so discovery has to be disabled.

```jsx
const iOS =
  typeof navigator !== 'undefined' && /iPad|iPhone|iPod/.test(navigator.userAgent);

<SwipeableDrawer disableBackdropTransition={!iOS} disableDiscovery={iOS} />;
```

### Swipeable edge

You can configure the `SwipeableDrawer` to have a visible edge when closed.

If you are on a desktop, you can toggle the drawer with the "OPEN" button.
If you are on mobile, you can open the demo in CodeSandbox ("edit" icon) and swipe.


### Keep mounted

The Modal used internally by the Swipeable Drawer has the `keepMounted` prop set by default.
This means that the contents of the drawer are always present in the DOM.

You can change this default behavior with the `ModalProps` prop, but you may encounter issues with `keepMounted: false` in React 18.

```jsx
<Drawer
  variant="temporary"
  ModalProps={{
    keepMounted: false,
  }}
/>
```

## Responsive drawer

You can use the `temporary` variant to display a drawer for small screens and `permanent` for a drawer for wider screens.


## Persistent drawer

Persistent navigation drawers can toggle open or closed.
The drawer sits on the same surface elevation as the content.
It is closed by default and opens by selecting the menu icon, and stays open until closed by the user.
The state of the drawer is remembered from action to action and session to session.

When the drawer is outside of the page grid and opens, the drawer forces other content to change size and adapt to the smaller viewport.

Persistent navigation drawers are acceptable for all sizes larger than mobile.
They are not recommended for apps with multiple levels of hierarchy that require using an up arrow for navigation.



## Mini variant drawer

In this variation, the persistent navigation drawer changes its width.
Its resting state is as a mini-drawer at the same elevation as the content, clipped by the app bar.
When expanded, it appears as the standard persistent navigation drawer.

The mini variant is recommended for apps sections that need quick selection access alongside content.


## Permanent drawer

Permanent navigation drawers are always visible and pinned to the left edge, at the same elevation as the content or background. They cannot be closed.

Permanent navigation drawers are the **recommended default for desktop**.

### Full-height navigation

Apps focused on information consumption that use a left-to-right hierarchy.



### Clipped under the app bar

Apps focused on productivity that require balance across the screen.



# Snackbars

---
productId: material-ui
title: React Snackbar component
components: Snackbar, SnackbarContent
githubLabel: 'scope: snackbar'
materialDesign: https://m2.material.io/components/snackbars
waiAria: https://www.w3.org/TR/wai-aria-1.1/#alert
githubSource: packages/mui-material/src/Snackbar
---

# Snackbar

Snackbars (also known as toasts) are used for brief notifications of processes that have been or will be performed.


## Introduction

The Snackbar component appears temporarily and floats above the UI to provide users with (non-critical) updates on an app's processes.
The demo below, inspired by Google Keep, shows a basic Snackbar with a text element and two actions:


### Usage

Snackbars differ from [Alerts](/material-ui/react-alert/) in that Snackbars have a fixed position and a high z-index, so they're intended to break out of the document flow; Alerts, on the other hand, are usually part of the flow—except when they're [used as children of a Snackbar](#use-with-alerts).

Snackbars also differ from [Dialogs](/material-ui/react-dialog/) in that Snackbars are not intended to convey _critical_ information or block the user from interacting with the rest of the app; Dialogs, by contrast, require input from the user in order to be dismissed.

## Basics

### Import

```jsx
import Snackbar from '@mui/material/Snackbar';
```

### Position

Use the `anchorOrigin` prop to control the Snackbar's position on the screen.


### Content

```jsx
import SnackbarContent from '@mui/material/SnackbarContent';
```

Use the Snackbar Content component to add text and actions to the Snackbar.


### Automatic dismiss

Use the `autoHideDuration` prop to automatically trigger the Snackbar's `onClose` function after a set period of time (in milliseconds).

Make sure to [provide sufficient time](https://www.w3.org/TR/UNDERSTANDING-WCAG20/time-limits.html) for the user to process the information displayed on it.


### Transitions

You can use the `TransitionComponent` prop to change the transition of the Snackbar from [Grow](/material-ui/transitions/#grow) (the default) to others such as [Slide](/material-ui/transitions/#slide).


## Customization

### Preventing default click away event

If you would like to prevent the default onClickAway behavior, you can set the event's `defaultMuiPrevented` property to `true`:

```jsx
<Snackbar
  slotProps={{
    clickAwayListener: {
      onClickAway: (event) => {
        // Prevent's default 'onClickAway' behavior.
        event.defaultMuiPrevented = true;
      },
    },
  }}
/>
```

### Use with Alerts

Use an Alert inside a Snackbar for messages that communicate a certain severity.


### Use with Floating Action Buttons

If you're using a [Floating Action Button](/material-ui/react-floating-action-button/) on mobile, Material Design recommends positioning snackbars directly above it, as shown in the demo below:


## Common examples

### Consecutive Snackbars

This demo shows how to display multiple Snackbars without stacking them by using a consecutive animation.


## Supplementary components

### notistack

![stars](https://img.shields.io/github/stars/iamhosseindhv/notistack.svg?style=social&label=Star)
![npm downloads](https://img.shields.io/npm/dm/notistack.svg)

With an imperative API, [notistack](https://github.com/iamhosseindhv/notistack) lets you vertically stack multiple Snackbars without having to handle their open and close states.
Even though this is discouraged in the Material Design guidelines, it is still a common pattern.


> **Warning:**
>
> Note that notistack prevents Snackbars from being [closed by pressing <kbd class="key">Escape</kbd>](#accessibility).


## Accessibility

The user should be able to dismiss Snackbars by pressing <kbd class="key">Escape</kbd>. If there are multiple instances appearing at the same time and you want <kbd class="key">Escape</kbd> to dismiss only the oldest one that's currently open, call `event.preventDefault` in the `onClose` prop.

```jsx
export default function MyComponent() {
  const [open, setOpen] = React.useState(true);

  return (
    <React.Fragment>
      <Snackbar
        open={open}
        onClose={(event, reason) => {
          // `reason === 'escapeKeyDown'` if `Escape` was pressed
          setOpen(false);
          // call `event.preventDefault` to only close one Snackbar at a time.
        }}
      />
      <Snackbar open={open} onClose={() => setOpen(false)} />
    </React.Fragment>
  );
}
```

## Anatomy

The Snackbar component is composed of a root `<div>` that houses interior elements like the Snackbar Content and other optional components (such as buttons or decorators).

```html
<div role="presentation" class="MuiSnackbar-root">
  <div class="MuiPaper-root MuiSnackbarContent-root" role="alert">
    <div class="MuiSnackbarContent-message">
      <!-- Snackbar content goes here -->
    </div>
  </div>
</div>
```


# Steppers

---
productId: material-ui
title: React Stepper component
components: MobileStepper, Step, StepButton, StepConnector, StepContent, StepIcon, StepLabel, Stepper
githubLabel: 'scope: stepper'
materialDesign: https://m1.material.io/components/steppers.html
githubSource: packages/mui-material/src/Stepper
---

# Stepper

Steppers convey progress through numbered steps. It provides a wizard-like workflow.

Steppers display progress through a sequence of logical and numbered steps. They may also be used for navigation.
Steppers may display a transient feedback message after a step is saved.

- **Types of Steps**: Editable, Non-editable, Mobile, Optional
- **Types of Steppers**: Horizontal, Vertical, Linear, Non-linear


> **Info:**
>
> This component is no longer documented in the [Material Design guidelines](https://m2.material.io/), but Material UI will continue to support it.


## Introduction

The Stepper component displays progress through a sequence of logical and numbered steps.
It supports horizontal and vertical orientation for desktop and mobile viewports.

Steppers are implemented using a collection of related components:

- Stepper: the container for the steps.
- Step: an individual step in the sequence.
- Step Label: a label for a Step.
- Step Content: optional content for a Step.
- Step Button: optional button for a Step.
- Step Icon: optional icon for a Step.
- Step Connector: optional customized connector between Steps.

## Basics

```jsx
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
```

## Horizontal stepper

Horizontal steppers are ideal when the contents of one step depend on an earlier step.

Avoid using long step names in horizontal steppers.

### Linear

A linear stepper allows the user to complete the steps in sequence.

The `Stepper` can be controlled by passing the current step index (zero-based) as the `activeStep` prop. `Stepper` orientation is set using the `orientation` prop.

This example also shows the use of an optional step by placing the `optional` prop on the second `Step` component. Note that it's up to you to manage when an optional step is skipped. Once you've determined this for a particular step you must set `completed={false}` to signify that even though the active step index has gone beyond the optional step, it's not actually complete.


### Non-linear

Non-linear steppers allow the user to enter a multi-step flow at any point.

This example is similar to the regular horizontal stepper, except steps are no longer automatically set to `disabled={true}` based on the `activeStep` prop.

The use of the `StepButton` here demonstrates clickable step labels, as well as setting the `completed`
flag. However because steps can be accessed in a non-linear fashion, it's up to your own implementation to
determine when all steps are completed (or even if they need to be completed).


### Alternative label

Labels can be placed below the step icon by setting the `alternativeLabel` prop on the `Stepper` component.


### Error step


### Customized horizontal stepper

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


## Vertical stepper

Vertical steppers are designed for narrow screen sizes. They are ideal for mobile. All the features of the horizontal stepper can be implemented.


### Performance

The content of a step is unmounted when closed.
If you need to make the content available to search engines or render expensive component trees inside your modal while optimizing for interaction responsiveness it might be a good idea to keep the step mounted with:

```jsx
<StepContent slotProps={{ transition: { unmountOnExit: false } }} />
```

## Mobile stepper

This component implements a compact stepper suitable for a mobile device. It has more limited functionality than the vertical stepper. See [mobile steps](https://m1.material.io/components/steppers.html#steppers-types-of-steps) for its inspiration.

The mobile stepper supports three variants to display progress through the available steps: text, dots, and progress.

### Text

The current step and total number of steps are displayed as text.


### Dots

Use dots when the number of steps is small.


### Progress

Use a progress bar when there are many steps, or if there are steps that need to be inserted during the process (based on responses to earlier steps).



# Selects

---
productId: material-ui
title: React Select component
components: Select, NativeSelect
githubLabel: 'scope: select'
materialDesign: https://m2.material.io/components/menus#exposed-dropdown-menu
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/combobox/examples/combobox-select-only/
githubSource: packages/mui-material/src/Select
---

# Select

Select components are used for collecting user provided information from a list of options.


## Basic select

Menus are positioned under their emitting elements, unless they are close to the bottom of the viewport.


## Advanced features

The Select component is meant to be interchangeable with a native `<select>` element.

If you are looking for more advanced features, like combobox, multiselect, autocomplete, async or creatable support, head to the [`Autocomplete` component](/material-ui/react-autocomplete/).
It's meant to be an improved version of the "react-select" and "downshift" packages.

## Props

The Select component is implemented as a custom `<input>` element of the [InputBase](/material-ui/api/input-base/).
It extends the [text field components](/material-ui/react-text-field/) subcomponents, either the [OutlinedInput](/material-ui/api/outlined-input/), [Input](/material-ui/api/input/), or [FilledInput](/material-ui/api/filled-input/), depending on the variant selected.
It shares the same styles and many of the same props. Refer to the respective component's API page for details.

> **Warning:**
>
> Unlike input components, the `placeholder` prop is not available in Select. To add a placeholder, refer to the [placeholder](#placeholder) section below.


### Filled and standard variants


### Labels and helper text


> **Warning:**
>
> Note that when using FormControl with the outlined variant of the Select, you need to provide a label in two places: in the InputLabel component and in the `label` prop of the Select component (see the above demo).


### Auto width


### Small Size


### Other props


## Native select

As the user experience can be improved on mobile using the native select of the platform,
we allow such pattern.


## TextField

The `TextField` wrapper component is a complete form control including a label, input and help text.
You can find an example with the select mode [in this section](/material-ui/react-text-field/#select).

## Customization

Here are some examples of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).

The first step is to style the `InputBase` component.
Once it's styled, you can either use it directly as a text field or provide it to the select `input` prop to have a `select` field.
Notice that the `"standard"` variant is easier to customize, since it does not wrap the contents in a `fieldset`/`legend` markup.


🎨 If you are looking for inspiration, you can check [MUI Treasury's customization examples](https://mui-treasury.com/?path=/docs/select-introduction--docs).

## Multiple select

The `Select` component can handle multiple selections.
It's enabled with the `multiple` prop.

Like with the single selection, you can pull out the new value by accessing `event.target.value` in the `onChange` callback. It's always an array.

### Default


### Selection indicators

This example demonstrates how icons are used to indicate the selection state of each item in the listbox.


### Chip


### Placeholder


### Native


## Controlling the open state

You can control the open state of the select with the `open` prop. Alternatively, it is also possible to set the initial (uncontrolled) open state of the component with the `defaultOpen` prop.

> **Info:**
>
> - A component is **controlled** when it's managed by its parent using props.
> - A component is **uncontrolled** when it's managed by its own local state.
> 
> Learn more about controlled and uncontrolled components in the [React documentation](https://react.dev/learn/sharing-state-between-components#controlled-and-uncontrolled-components).



## With a dialog

While it's discouraged by the Material Design guidelines, you can use a select inside a dialog.


## Grouping

Display categories with the `ListSubheader` component or the native `<optgroup>` element.


> **Warning:**
>
> If you wish to wrap the ListSubheader in a custom component, you'll have to annotate it so Material UI can handle it properly when determining focusable elements.
> 
> You have two options for solving this:
> Option 1: Define a static boolean field called `muiSkipListHighlight` on your component function, and set it to `true`:
> 
> ```tsx
> function MyListSubheader(props: ListSubheaderProps) {
>   return <ListSubheader {...props} />;
> }
> 
> MyListSubheader.muiSkipListHighlight = true;
> export default MyListSubheader;
> 
> // elsewhere:
> 
> return (
>   <Select>
>     <MyListSubheader>Group 1</MyListSubheader>
>     <MenuItem value={1}>Option 1</MenuItem>
>     <MenuItem value={2}>Option 2</MenuItem>
>     <MyListSubheader>Group 2</MyListSubheader>
>     <MenuItem value={3}>Option 3</MenuItem>
>     <MenuItem value={4}>Option 4</MenuItem>
>     {/* ... */}
>   </Select>
> ```
> 
> Option 2: Place a `muiSkipListHighlight` prop on each instance of your component.
> The prop doesn't have to be forwarded to the ListSubheader, nor present in the underlying DOM element.
> It just has to be placed on a component that's used as a subheader.
> 
> ```tsx
> export default function MyListSubheader(
>   props: ListSubheaderProps & { muiSkipListHighlight: boolean },
> ) {
>   const { muiSkipListHighlight, ...other } = props;
>   return <ListSubheader {...other} />;
> }
> 
> // elsewhere:
> 
> return (
>   <Select>
>     <MyListSubheader muiSkipListHighlight>Group 1</MyListSubheader>
>     <MenuItem value={1}>Option 1</MenuItem>
>     <MenuItem value={2}>Option 2</MenuItem>
>     <MyListSubheader muiSkipListHighlight>Group 2</MyListSubheader>
>     <MenuItem value={3}>Option 3</MenuItem>
>     <MenuItem value={4}>Option 4</MenuItem>
>     {/* ... */}
>   </Select>
> );
> ```
> 
> We recommend the first option as it doesn't require updating all the usage sites of the component.
> 
> Keep in mind this is **only necessary** if you wrap the ListSubheader in a custom component.
> If you use the ListSubheader directly, **no additional code is required**.


## Accessibility

To properly label your `Select` input you need an extra element with an `id` that contains a label.
That `id` needs to match the `labelId` of the `Select`, for example:

```jsx
<InputLabel id="label">Age</InputLabel>
<Select labelId="label" id="select" value="20">
  <MenuItem value="10">Ten</MenuItem>
  <MenuItem value="20">Twenty</MenuItem>
</Select>
```

Alternatively a `TextField` with an `id` and `label` creates the proper markup and
ids for you:

```jsx
<TextField id="select" label="Age" value="20" select>
  <MenuItem value="10">Ten</MenuItem>
  <MenuItem value="20">Twenty</MenuItem>
</TextField>
```

For a [native select](#native-select), you should mention a label by giving the value of the `id` attribute of the select element to the `InputLabel`'s `htmlFor` attribute:

```jsx
<InputLabel htmlFor="select">Age</InputLabel>
<NativeSelect id="select">
  <option value="10">Ten</option>
  <option value="20">Twenty</option>
</NativeSelect>
```
