---
title: Mui Input Components
source: mui.com/material-ui
syllabus_weeks: [11]
topics: [TextField, variants, validation, adornments, Checkbox, Radio, Switch, Slider, Rating, Button, IconButton, FAB, ToggleButton, NumberField]
---



# Text Fields

---
productId: material-ui
title: React Text Field component
components: FilledInput, FormControl, FormHelperText, Input, InputAdornment, InputBase, InputLabel, OutlinedInput, TextField
githubLabel: 'scope: text field'
materialDesign: https://m2.material.io/components/text-fields
githubSource: packages/mui-material/src/TextField
---

# Text Field

Text Fields let users enter and edit text.

Text fields allow users to enter text into a UI. They typically appear in forms and dialogs.


## Basic TextField

The `TextField` wrapper component is a complete form control including a label, input, and help text.
It comes with three variants: outlined (default), filled, and standard.


> **Info:**
>
> The standard variant of the Text Field is no longer documented in the [Material Design guidelines](https://m2.material.io/)
> ([this article explains why](https://medium.com/google-design/the-evolution-of-material-designs-text-fields-603688b3fe03)),
> but Material UI will continue to support it.


## Form props

Standard form attributes are supported, for example `required`, `disabled`, `type`, etc. as well as a `helperText` which is used to give context about a field's input, such as how the input will be used.


## Controlling the HTML input

Use `slotProps.htmlInput` to pass attributes to the underlying `<input>` element.

```jsx
<TextField slotProps={{ htmlInput: { 'data-testid': '…' } }} />
```

The rendered HTML input will look like this:

```html
<input
  aria-invalid="false"
  class="MuiInputBase-input MuiOutlinedInput-input"
  type="text"
  data-testid="…"
/>
```

> **Warning:**
>
> `slotProps.htmlInput` is not the same as `slotProps.input`.
> `slotProps.input` refers to the React `<Input />` component that's rendered based on the specified variant prop.
> `slotProps.htmlInput` refers to the HTML `<input>` element rendered within that Input component, regardless of the variant.


## Validation

The `error` prop toggles the error state.
The `helperText` prop can then be used to provide feedback to the user about the error.


## Multiline

The `multiline` prop transforms the Text Field into a [Textarea Autosize](/material-ui/react-textarea-autosize/) element.
Unless the `rows` prop is set, the height of the text field dynamically matches its content.
You can use the `minRows` and `maxRows` props to bound it.


## Select

The `select` prop makes the text field use the [Select](/material-ui/react-select/) component internally.


## Icons

There are multiple ways to display an icon with a text field.


### Input Adornments

The main way is with an `InputAdornment`.
This can be used to add a prefix, a suffix, or an action to an input.
For instance, you can use an icon button to hide or reveal the password.


#### Customizing adornments

You can apply custom styles to adornments, and trigger changes to one based on attributes from another.
For example, the demo below uses the label's `[data-shrink=true]` attribute to make the suffix visible (via opacity) when the label is in its shrunken state.


## Sizes

Fancy smaller inputs? Use the `size` prop.


The `filled` variant input height can be further reduced by rendering the label outside of it.


## Margin

The `margin` prop can be used to alter the vertical spacing of the text field.
Using `none` (default) doesn't apply margins to the `FormControl` whereas `dense` and `normal` do.


## Full width

`fullWidth` can be used to make the input take up the full width of its container.


## Uncontrolled vs. Controlled

The component can be controlled or uncontrolled.

> **Info:**
>
> - A component is **controlled** when it's managed by its parent using props.
> - A component is **uncontrolled** when it's managed by its own local state.
> 
> Learn more about controlled and uncontrolled components in the [React documentation](https://react.dev/learn/sharing-state-between-components#controlled-and-uncontrolled-components).



## Components

`TextField` is composed of smaller components (
[`FormControl`](/material-ui/api/form-control/),
[`Input`](/material-ui/api/input/),
[`FilledInput`](/material-ui/api/filled-input/),
[`InputLabel`](/material-ui/api/input-label/),
[`OutlinedInput`](/material-ui/api/outlined-input/),
and [`FormHelperText`](/material-ui/api/form-helper-text/)
) that you can leverage directly to significantly customize your form inputs.

You might also have noticed that some native HTML input properties are missing from the `TextField` component.
This is on purpose.
The component takes care of the most used properties.
Then, it's up to the user to use the underlying component shown in the following demo. Still, you can use `slotProps.htmlInput` (and `slotProps.input`, `slotProps.inputLabel` properties) if you want to avoid some boilerplate.


## Inputs


## Color

The `color` prop changes the highlight color of the text field when focused.


## Customization

Here are some examples of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).

### Using the styled API


### Using the theme style overrides API

Use the `styleOverrides` key to change any style injected by Material UI into the DOM.
See the [theme style overrides](/material-ui/customization/theme-components/#theme-style-overrides) documentation for further details.


Customization does not stop at CSS.
You can use composition to build custom components and give your app a unique feel.
Below is an example using the [`InputBase`](/material-ui/api/input-base/) component, inspired by Google Maps.


🎨 If you are looking for inspiration, you can check [MUI Treasury's customization examples](https://mui-treasury.com/?path=/docs/textField-introduction--docs).

## `useFormControl`

For advanced customization use cases, a `useFormControl()` hook is exposed.
This hook returns the context value of the parent `FormControl` component.

**API**

```jsx
import { useFormControl } from '@mui/material/FormControl';
```

**Returns**

`value` (_object_):

- `value.adornedStart` (_bool_): Indicate whether the child `Input` or `Select` component has a start adornment.
- `value.setAdornedStart` (_func_): Setter function for `adornedStart` state value.
- `value.color` (_string_): The theme color is being used, inherited from `FormControl` `color` prop .
- `value.disabled` (_bool_): Indicate whether the component is being displayed in a disabled state, inherited from `FormControl` `disabled` prop.
- `value.error` (_bool_): Indicate whether the component is being displayed in an error state, inherited from `FormControl` `error` prop
- `value.filled` (_bool_): Indicate whether input is filled
- `value.focused` (_bool_): Indicate whether the component and its children are being displayed in a focused state
- `value.fullWidth` (_bool_): Indicate whether the component is taking up the full width of its container, inherited from `FormControl` `fullWidth` prop
- `value.hiddenLabel` (_bool_): Indicate whether the label is being hidden, inherited from `FormControl` `hiddenLabel` prop
- `value.required` (_bool_): Indicate whether the label is indicating that the input is required input, inherited from the `FormControl` `required` prop
- `value.size` (_string_): The size of the component, inherited from the `FormControl` `size` prop
- `value.variant` (_string_): The variant is being used by the `FormControl` component and its children, inherited from `FormControl` `variant` prop
- `value.onBlur` (_func_): Should be called when the input is blurred
- `value.onFocus` (_func_): Should be called when the input is focused
- `value.onEmpty` (_func_): Should be called when the input is emptied
- `value.onFilled` (_func_): Should be called when the input is filled

**Example**


## Performance

Global styles for the auto-fill keyframes are injected and removed on each mount and unmount, respectively.
If you are loading a large number of Text Field components at once, it might be a good idea to change this default behavior by enabling [`disableInjectingGlobalStyles`](/material-ui/api/input-base/#input-base-prop-disableInjectingGlobalStyles) in `MuiInputBase`.
Make sure to inject `GlobalStyles` for the auto-fill keyframes at the top of your application.

```jsx
import { GlobalStyles, createTheme, ThemeProvider } from '@mui/material';

const theme = createTheme({
  components: {
    MuiInputBase: {
      defaultProps: {
        disableInjectingGlobalStyles: true,
      },
    },
  },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles
        styles={{
          '@keyframes mui-auto-fill': { from: { display: 'block' } },
          '@keyframes mui-auto-fill-cancel': { from: { display: 'block' } },
        }}
      />
      ...
    </ThemeProvider>
  );
}
```

## Limitations

### Shrink

The input label "shrink" state isn't always correct.
The input label is supposed to shrink as soon as the input is displaying something.
In some circumstances, we can't determine the "shrink" state (datetime input, Stripe input). You might notice an overlap.

![shrink](/static/images/text-fields/shrink.png)

To workaround the issue, you can force the "shrink" state of the label.

```jsx
<TextField slotProps={{ inputLabel: { shrink: true } }} />
```

or

```jsx
<InputLabel shrink>Count</InputLabel>
```

### Floating label

The floating label is absolutely positioned.
It won't impact the layout of the page.
Make sure that the input is larger than the label to display correctly.

### type="number"

:::warning
We do not recommend using `type="number"` with a Text Field due to potential usability issues:

- it allows certain non-numeric characters ('e', '+', '-', '.') and silently discards others
- the functionality of scrolling to increment/decrement the number can cause accidental and hard-to-notice changes
- and more—see [Why the GOV.UK Design System team changed the input type for numbers](https://technology.blog.gov.uk/2020/02/24/why-the-gov-uk-design-system-team-changed-the-input-type-for-numbers/) for a more detailed explanation of the limitations of `<input type="number">`

  :::

If you need a text field with number validation, you can use [Number Field](/material-ui/react-number-field/) instead.

### Helper text

The helper text prop affects the height of the text field. If two text fields are placed side by side, one with a helper text and one without, they will have different heights. For example:


This can be fixed by passing a space character to the `helperText` prop:


## Integration with 3rd party input libraries

You can use third-party libraries to format an input.
You have to provide a custom implementation of the `<input>` element with the `inputComponent` property.

The following demo uses the [react-imask](https://github.com/uNmAnNeR/imaskjs) and [react-number-format](https://github.com/s-yadav/react-number-format) libraries. The same concept could be applied to, for example [react-stripe-element](https://github.com/mui/material-ui/issues/16037).


The provided input component should expose a ref with a value that implements the following interface:

```ts
interface InputElement {
  focus(): void;
  value?: string;
}
```

```jsx
const MyInputComponent = React.forwardRef((props, ref) => {
  const { component: Component, ...other } = props;

  // implement `InputElement` interface
  React.useImperativeHandle(ref, () => ({
    focus: () => {
      // logic to focus the rendered component from 3rd party belongs here
    },
    // hiding the value e.g. react-stripe-elements
  }));

  // `Component` will be your `SomeThirdPartyComponent` from below
  return <Component {...other} />;
});

// usage
<TextField
  slotProps={{
    input: {
      inputComponent: MyInputComponent,
      inputProps: {
        component: SomeThirdPartyComponent,
      },
    },
  }}
/>;
```

## Accessibility

In order for the text field to be accessible, **the input should be linked to the label and the helper text**. The underlying DOM nodes should have this structure:

```jsx
<div class="form-control">
  <label for="my-input">Email address</label>
  <input id="my-input" aria-describedby="my-helper-text" />
  <span id="my-helper-text">We'll never share your email.</span>
</div>
```

- If you are using the `TextField` component, you just have to provide a unique `id` unless you're using the `TextField` only client-side.
  Until the UI is hydrated `TextField` without an explicit `id` will not have associated labels.
- If you are composing the component:

```jsx
<FormControl>
  <InputLabel htmlFor="my-input">Email address</InputLabel>
  <Input id="my-input" aria-describedby="my-helper-text" />
  <FormHelperText id="my-helper-text">We'll never share your email.</FormHelperText>
</FormControl>
```

## Supplementary projects

<!-- To sync with related-projects.md -->

For more advanced use cases, you might be able to take advantage of:

- [react-hook-form-mui](https://github.com/dohomi/react-hook-form-mui): Material UI and [react-hook-form](https://react-hook-form.com/) combined.
- [formik-material-ui](https://github.com/stackworx/formik-mui): Bindings for using Material UI with [formik](https://formik.org/).
- [mui-rff](https://github.com/lookfirst/mui-rff): Bindings for using Material UI with [React Final Form](https://final-form.org/react).
- [@ui-schema/ds-material](https://www.npmjs.com/package/@ui-schema/ds-material) Bindings for using Material UI with [UI Schema](https://github.com/ui-schema/ui-schema). JSON Schema compatible.


# Checkboxes

---
productId: material-ui
title: React Checkbox component
components: Checkbox, FormControl, FormGroup, FormLabel, FormControlLabel
materialDesign: https://m2.material.io/components/selection-controls#checkboxes
githubLabel: 'scope: checkbox'
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/checkbox/
githubSource: packages/mui-material/src/Checkbox
---

# Checkbox

Checkboxes allow the user to select one or more items from a set.

Checkboxes can be used to turn an option on or off.

If you have multiple options appearing in a list,
you can preserve space by using checkboxes instead of on/off switches.
If you have a single option, avoid using a checkbox and use an on/off switch instead.


## Basic checkboxes


## Label

You can provide a label to the `Checkbox` thanks to the `FormControlLabel` component.


## Size

Use the `size` prop or customize the font size of the svg icons to change the size of the checkboxes.


## Color


## Icon


## Controlled

You can control the checkbox with the `checked` and `onChange` props:


## Indeterminate

A checkbox input can only have two states in a form: checked or unchecked.
It either submits its value or doesn't.
Visually, there are **three** states a checkbox can be in: checked, unchecked, or indeterminate.

You can change the indeterminate icon using the `indeterminateIcon` prop.


> **Warning:**
>
> When indeterminate is set, the value of the `checked` prop only impacts the form submitted values.
> It has no accessibility or UX implications.


## FormGroup

`FormGroup` is a helpful wrapper used to group selection control components.


## Label placement

You can change the placement of the label:


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


🎨 If you are looking for inspiration, you can check [MUI Treasury's customization examples](https://mui-treasury.com/?path=/docs/checkbox-introduction--docs).

## When to use

- [Checkboxes vs. Radio Buttons](https://www.nngroup.com/articles/checkboxes-vs-radio-buttons/)
- [Checkboxes vs. Switches](https://uxplanet.org/checkbox-vs-toggle-switch-7fc6e83f10b8)

## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/checkbox/)

- All form controls should have labels, and this includes radio buttons, checkboxes, and switches. In most cases, this is done by using the `<label>` element ([FormControlLabel](/material-ui/api/form-control-label/)).
- When a label can't be used, it's necessary to add an attribute directly to the input component.
  In this case, you can apply the additional attribute (for example `aria-label`, `aria-labelledby`, `title`) via the `slotProps.input` prop.

```jsx
<Checkbox
  value="checkedA"
  slotProps={{
    input: { 'aria-label': 'Checkbox A' },
  }}
/>
```


# Radio Buttons

---
productId: material-ui
title: React Radio Group component
components: Radio, RadioGroup, FormControl, FormLabel, FormControlLabel
githubLabel: 'scope: radio'
materialDesign: https://m2.material.io/components/selection-controls#radio-buttons
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/radio/
githubSource: packages/mui-material/src/RadioGroup
---

# Radio Group

The Radio Group allows the user to select one option from a set.

Use radio buttons when the user needs to see all available options.
If available options can be collapsed, consider using a [Select component](/material-ui/react-select/) because it uses less space.

Radio buttons should have the most commonly used option selected by default.


## Radio group

`RadioGroup` is a helpful wrapper used to group `Radio` components that provides an easier API, and proper keyboard accessibility to the group.


### Direction

To lay out the buttons horizontally, set the `row` prop:


### Controlled

You can control the radio with the `value` and `onChange` props:


## Standalone radio buttons

`Radio` can also be used standalone, without the RadioGroup wrapper.


## Size

Use the `size` prop or customize the font size of the svg icons to change the size of the radios.


## Color


## Label placement

You can change the placement of the label with the `FormControlLabel` component's `labelPlacement` prop:


## Show error

In general, radio buttons should have a value selected by default. If this is not the case, you can display an error if no value is selected when the form is submitted:


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


## `useRadioGroup`

For advanced customization use cases, a `useRadioGroup()` hook is exposed.
It returns the context value of the parent radio group.
The Radio component uses this hook internally.

### API

```jsx
import { useRadioGroup } from '@mui/material/RadioGroup';
```

#### Returns

`value` (_object_):

- `value.name` (_string_ [optional]): The name used to reference the value of the control.
- `value.onChange` (_func_ [optional]): Callback fired when a radio button is selected.
- `value.value` (_any_ [optional]): Value of the selected radio button.

#### Example


## When to use

- [Checkboxes vs. Radio Buttons](https://www.nngroup.com/articles/checkboxes-vs-radio-buttons/)

## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/radio/)

- All form controls should have labels, and this includes radio buttons, checkboxes, and switches. In most cases, this is done by using the `<label>` element ([FormControlLabel](/material-ui/api/form-control-label/)).

- When a label can't be used, it's necessary to add an attribute directly to the input component.
  In this case, you can apply the additional attribute (for example `aria-label`, `aria-labelledby`, `title`) via the `inputProps` property.

```jsx
<Radio
  value="radioA"
  inputProps={{
    'aria-label': 'Radio A',
  }}
/>
```


# Switches

---
productId: material-ui
title: React Switch component
components: Switch, FormControl, FormGroup, FormLabel, FormControlLabel
githubLabel: 'scope: switch'
materialDesign: https://m2.material.io/components/selection-controls#switches
githubSource: packages/mui-material/src/Switch
---

# Switch

Switches toggle the state of a single setting on or off.

Switches are the preferred way to adjust settings on mobile.
The option that the switch controls, as well as the state it's in,
should be made clear from the corresponding inline label.


## Basic switches


## Label

You can provide a label to the `Switch` thanks to the `FormControlLabel` component.


## Size

Use the `size` prop to change the size of the switch.


## Color


## Controlled

You can control the switch with the `checked` and `onChange` props:


## Switches with FormGroup

`FormGroup` is a helpful wrapper used to group selection controls components that provides an easier API.
However, you are encouraged to use [Checkboxes](/material-ui/react-checkbox/) instead if multiple related controls are required. (See: [When to use](#when-to-use)).


## Customization

Here are some examples of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


🎨 If you are looking for inspiration, you can check [MUI Treasury's customization examples](https://www.mui-treasury.com/?path=/docs/switch-introduction--docs).

## Label placement

You can change the placement of the label:


## When to use

- [Checkboxes vs. Switches](https://uxplanet.org/checkbox-vs-toggle-switch-7fc6e83f10b8)

## Accessibility

- All form controls should have labels, and this includes radio buttons, checkboxes, and switches. In most cases, this is done by using the `<label>` element ([FormControlLabel](/material-ui/api/form-control-label/)).
- When a label can't be used, it's necessary to add an attribute directly to the input component.
  In this case, you can apply the additional attribute (for example `aria-label`, `aria-labelledby`, `title`) via the `inputProps` prop.

```jsx
<Switch value="checkedA" inputProps={{ 'aria-label': 'Switch A' }} />
```


# Slider

---
productId: material-ui
title: React Slider component
components: Slider
githubLabel: 'scope: slider'
materialDesign: https://m2.material.io/components/sliders
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/slider-multithumb/
githubSource: packages/mui-material/src/Slider
---

# Slider

Sliders allow users to make selections from a range of values.

Sliders reflect a range of values along a bar, from which users may select a single value. They are ideal for adjusting settings such as volume, brightness, or applying image filters.


## Continuous sliders

Continuous sliders allow users to select a value along a subjective range.


## Sizes

For smaller slider, use the prop `size="small"`.


## Discrete sliders

Discrete sliders can be adjusted to a specific value by referencing its value indicator.
You can generate a mark for each step with `marks={true}`.


### Small steps

You can change the default step increment.
Make sure to adjust the `shiftStep` prop (the granularity with which the slider can step when using Page Up/Down or Shift + Arrow Up/Down) to a value divisible by the `step`.


### Custom marks

You can have custom marks by providing a rich array to the `marks` prop.


### Restricted values

You can restrict the selectable values to those provided with the `marks` prop with `step={null}`.


### Label always visible

You can force the thumb label to be always visible with `valueLabelDisplay="on"`.


## Range slider

The slider can be used to set the start and end of a range by supplying an array of values to the `value` prop.


### Minimum distance

You can enforce a minimum distance between values in the `onChange` event handler.
By default, when you move the pointer over a thumb while dragging another thumb, the active thumb will swap to the hovered thumb. You can disable this behavior with the `disableSwap` prop.
If you want the range to shift when reaching minimum distance, you can utilize the `activeThumb` parameter in `onChange`.


## Slider with input field

In this example, an input allows a discrete value to be set.


## Color


## Customization

Here are some examples of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


### Music player


## Vertical sliders

Set the `orientation` prop to `"vertical"` to create vertical sliders. The thumb will track vertical movement instead of horizontal movement.


> **Warning:**
>
> Chrome versions below 124 implement `aria-orientation` incorrectly for vertical sliders and expose them as `'horizontal'` in the accessibility tree. ([Chromium issue #40736841](https://issues.chromium.org/issues/40736841))
> 
> The `-webkit-appearance: slider-vertical` CSS property can be used to correct this for these older versions, with the trade-off of causing a console warning in newer Chrome versions:
> 
> ```css
> .MuiSlider-thumb input {
>   -webkit-appearance: slider-vertical;
> }
> ```


## Marks placement

You can customize your slider by adding and repositioning marks for minimum and maximum values.


## Track

The track shows the range available for user selection.

### Removed track

The track can be turned off with `track={false}`.


### Inverted track

The track can be inverted with `track="inverted"`.


## Non-linear scale

You can use the `scale` prop to represent the `value` on a different scale.

In the following demo, the value _x_ represents the value _2^x_.
Increasing _x_ by one increases the represented value by factor _2_.


## Accessibility

(WAI-ARIA: https://www.w3.org/WAI/ARIA/apg/patterns/slider-multithumb/)

The component handles most of the work necessary to make it accessible.
However, you need to make sure that:

- Each thumb has a user-friendly label (`aria-label`, `aria-labelledby` or `getAriaLabel` prop).
- Each thumb has a user-friendly text for its current value.
  This is not required if the value matches the semantics of the label.
  You can change the name with the `getAriaValueText` or `aria-valuetext` prop.


# Rating

---
productId: material-ui
title: React Rating component
components: Rating
githubLabel: 'scope: rating'
waiAria: https://www.w3.org/WAI/tutorials/forms/custom-controls/#a-star-rating
githubSource: packages/mui-material/src/Rating
---

# Rating

Ratings provide insight regarding others' opinions and experiences, and can allow the user to submit a rating of their own.


## Basic rating


## Rating precision

The rating can display any float number with the `value` prop.
Use the `precision` prop to define the minimum increment value change allowed.


## Hover feedback

You can display a label on hover to help the user pick the correct rating value.
The demo uses the `onChangeActive` prop.


## Sizes

For larger or smaller ratings use the `size` prop.


## Customization

Here are some examples of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


## Radio group

The rating is implemented with a radio group, set `highlightSelectedOnly` to restore the natural behavior.


## Accessibility

([WAI tutorial](https://www.w3.org/WAI/tutorials/forms/custom-controls/#a-star-rating))

The accessibility of this component relies on:

- A radio group with its fields visually hidden.
  It contains six radio buttons, one for each star, and another for 0 stars that is checked by default. Be sure to provide a value for the `name` prop that is unique to the parent form.
- Labels for the radio buttons containing actual text ("1 Star", "2 Stars", …).
  Be sure to provide a suitable function to the `getLabelText` prop when the page is in a language other than English. You can use the [included locales](/material-ui/guides/localization/), or provide your own.
- A visually distinct appearance for the rating icons.
  By default, the rating component uses both a difference of color and shape (filled and empty icons) to indicate the value. In the event that you are using color as the only means to indicate the value, the information should also be also displayed as text, as in this demo. This is important to match [success Criterion 1.4.1](https://www.w3.org/TR/WCAG21/#use-of-color) of WCAG2.1.


### ARIA

The read only rating has a role of "img", and an aria-label that describes the displayed rating.

### Keyboard

Because the rating component uses radio buttons, keyboard interaction follows the native browser behavior. Tab will focus the current rating, and cursor keys control the selected rating.

The read only rating is not focusable.

## Testing

When testing the Rating component in environments such as Jest with jsdom, certain user interactions—especially hover-based interactions—may not behave as expected.
This is because the component relies on `getBoundingClientRect()` to calculate the position of each icon and determine which icon is currently being hovered.
In jsdom, `getBoundingClientRect()` returns `0` values by default, which can lead to incorrect behavior such as `NaN` being passed to the `onChange` handler.

To avoid this issue in your test suite:

- Prefer `fireEvent` over `userEvent` when simulating click events.
- Avoid relying on hover behavior to trigger changes.
- If needed, mock `getBoundingClientRect()` manually for more advanced interactions.

```tsx
// @vitest-environment jsdom

import { Rating } from '@mui/material';
import { render, fireEvent, screen } from '@testing-library/react';

import { describe, test, vi } from 'vitest';

describe('Rating', () => {
  test('should update rating on click', () => {
    const handleChange = vi.fn();
    render(<Rating onChange={(_, newValue) => handleChange(newValue)} />);

    fireEvent.click(screen.getByLabelText('2 Stars'));

    expect(handleChange).toHaveBeenCalledWith(2);
  });
});
```


# Buttons

---
productId: material-ui
title: React Button component
components: Button, IconButton, ButtonBase
materialDesign: https://m2.material.io/components/buttons
githubLabel: 'scope: button'
waiAria: https://www.w3.org/WAI/ARIA/apg/patterns/button/
githubSource: packages/mui-material/src/Button
---

# Button

Buttons allow users to take actions, and make choices, with a single tap.

Buttons communicate actions that users can take. They are typically placed throughout your UI, in places like:

- Modal windows
- Forms
- Cards
- Toolbars


## Basic button

The `Button` comes with three variants: text (default), contained, and outlined.


### Text button

[Text buttons](https://m2.material.io/components/buttons#text-button)
are typically used for less-pronounced actions, including those located: in dialogs, in cards.
In cards, text buttons help maintain an emphasis on card content.


### Contained button

[Contained buttons](https://m2.material.io/components/buttons#contained-button)
are high-emphasis, distinguished by their use of elevation and fill.
They contain actions that are primary to your app.


You can remove the elevation with the `disableElevation` prop.


### Outlined button

[Outlined buttons](https://m2.material.io/components/buttons#outlined-button) are medium-emphasis buttons.
They contain actions that are important but aren't the primary action in an app.

Outlined buttons are also a lower emphasis alternative to contained buttons,
or a higher emphasis alternative to text buttons.


## Handling clicks

All components accept an `onClick` handler that is applied to the root DOM element.

```jsx
<Button
  onClick={() => {
    alert('clicked');
  }}
>
  Click me
</Button>
```

Note that the documentation [avoids](/material-ui/guides/api/#native-properties) mentioning native props (there are a lot) in the API section of the components.

## Color


In addition to using the default button colors, you can add custom ones, or disable any you don't need. See the [Adding new colors](/material-ui/customization/palette/#custom-colors) examples for more info.

## Sizes

For larger or smaller buttons, use the `size` prop.


## Buttons with icons and label

Sometimes you might want to have icons for certain buttons to enhance the UX of the application as we recognize logos more easily than plain text. For example, if you have a delete button you can label it with a dustbin icon.


## Icon button

Icon buttons are commonly found in app bars and toolbars.

Icons are also appropriate for toggle buttons that allow a single choice to be selected or
deselected, such as adding or removing a star to an item.


### Sizes

For larger or smaller icon buttons, use the `size` prop.


### Colors

Use `color` prop to apply theme color palette to component.


### Loading

Starting from v6.4.0, use `loading` prop to set icon buttons in a loading state and disable interactions.


### Badge

You can use the [`Badge`](/material-ui/react-badge/) component to add a badge to an `IconButton`.


## File upload

To create a file upload button, turn the button into a label using `component="label"` and then create a visually-hidden input with type `file`.


## Loading

Starting from v6.4.0, use the `loading` prop to set buttons in a loading state and disable interactions.


Toggle the loading switch to see the transition between the different states.


> **Warning:**
>
> When the `loading` prop is set to `boolean`, the loading wrapper is always present in the DOM to prevent a [Google Translation Crash](https://github.com/mui/material-ui/issues/27853).
> 
> The `loading` value should always be `null` or `boolean`. The pattern below is not recommended as it can cause the Google Translation crash:
> 
> ```jsx
> <Button {...(isFetching && { loading: true })}> // ❌ Don't do this
> ```


## Customization

Here are some examples of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


🎨 If you are looking for inspiration, you can check [MUI Treasury's customization examples](https://mui-treasury.com/?path=/docs/button-introduction--docs).

## Complex button

The Text Buttons, Contained Buttons, Floating Action Buttons and Icon Buttons are built on top of the same component: the `ButtonBase`.
You can take advantage of this lower-level component to build custom interactions.


## Third-party routing library

One frequent use case is to perform navigation on the client only, without an HTTP round-trip to the server.
The `ButtonBase` component provides the `component` prop to handle this use case.
Here is a [more detailed guide](/material-ui/integrations/routing/#button).

## Limitations

### Cursor not-allowed

The ButtonBase component sets `pointer-events: none;` on disabled buttons, which prevents the appearance of a disabled cursor.

If you wish to use `not-allowed`, you have two options:

1. **CSS only**. You can remove the pointer-events style on the disabled state of the `<button>` element:

```css
.MuiButtonBase-root:disabled {
  cursor: not-allowed;
  pointer-events: auto;
}
```

However:

- You should add `pointer-events: none;` back when you need to display [tooltips on disabled elements](/material-ui/react-tooltip/#disabled-elements).
- The cursor won't change if you render something other than a button element, for instance, a link `<a>` element.

2. **DOM change**. You can wrap the button:

```jsx
<span style={{ cursor: 'not-allowed' }}>
  <Button component={Link} disabled>
    disabled
  </Button>
</span>
```

This has the advantage of supporting any element, for instance, a link `<a>` element.


# Button Group

---
productId: material-ui
title: React Button Group component
components: Button, ButtonGroup
githubLabel: 'component: ButtonGroup'
githubSource: packages/mui-material/src/ButtonGroup
---

# Button Group

The ButtonGroup component can be used to group related buttons.


## Basic button group

The buttons can be grouped by wrapping them with the `ButtonGroup` component.
They need to be immediate children.


## Button variants

All the standard button variants are supported.


## Sizes and colors

The `size` and `color` props can be used to control the appearance of the button group.


## Vertical group

The button group can be displayed vertically using the `orientation` prop.


## Split button

`ButtonGroup` can also be used to create a split button. The dropdown can change the button action (as in this example) or be used to immediately trigger a related action.


## Disabled elevation

You can remove the elevation with the `disableElevation` prop.


## Loading

Use the `loading` prop from `Button` to set buttons in a loading state and disable interactions.



# Floating Action Button

---
productId: material-ui
title: React Floating Action Button (FAB) component
components: Fab
githubLabel: 'component: Fab'
materialDesign: https://m2.material.io/components/buttons-floating-action-button
githubSource: packages/mui-material/src/Fab
---

# Floating Action Button

A Floating Action Button (FAB) performs the primary, or most common, action on a screen.

A floating action button appears in front of all screen content, typically as a circular shape with an icon in its center.
FABs come in two types: regular, and extended.

Only use a FAB if it is the most suitable way to present a screen's primary action.
Only one component is recommended per screen to represent the most common action.


## Basic FAB


## Size

By default, the size is `large`. Use the `size` prop for smaller floating action buttons.



## Animation

The floating action button animates onto the screen as an expanding piece of material, by default.

A floating action button that spans multiple lateral screens (such as tabbed screens) should briefly disappear,
then reappear if its action changes.

The Zoom transition can be used to achieve this. Note that since both the exiting and entering
animations are triggered at the same time, we use `enterDelay` to allow the outgoing Floating Action Button's
animation to finish before the new one enters.



# Toggle Button

---
productId: material-ui
title: Toggle Button React component
components: ToggleButton, ToggleButtonGroup
githubLabel: 'scope: toggle button'
materialDesign: https://m2.material.io/components/buttons#toggle-button
githubSource: packages/mui-material/src/ToggleButton
---

# Toggle Button

A Toggle Button can be used to group related options.

To emphasize groups of related Toggle buttons,
a group should share a common container.
The `ToggleButtonGroup` controls the selected state of its child buttons when given its own `value` prop.


## Exclusive selection

With exclusive selection, selecting one option deselects any other.

In this example, text justification toggle buttons present options for left, center, right, and fully justified text (disabled), with only one item available for selection at a time.

**Note**: Exclusive selection does not enforce that a button must be active. For that effect see [enforce value set](#enforce-value-set).


## Multiple selection

Multiple selection allows for logically-grouped options, like bold, italic, and underline, to have multiple options selected.


## Size

For larger or smaller buttons, use the `size` prop.


## Color


## Vertical buttons

The buttons can be stacked vertically with the `orientation` prop set to "vertical".


## Enforce value set

If you want to enforce that at least one button must be active, you can adapt your handleChange function.

```jsx
const handleAlignment = (event, newAlignment) => {
  if (newAlignment !== null) {
    setAlignment(newAlignment);
  }
};

const handleDevices = (event, newDevices) => {
  if (newDevices.length) {
    setDevices(newDevices);
  }
};
```


## Standalone toggle button


## Customization

Here is an example of customizing the component.
You can learn more about this in the [overrides documentation page](/material-ui/customization/how-to-customize/).


### Spacing

The demos below show how to adjust spacing between toggle buttons in horizontal and vertical orientations.

#### Horizontal Spacing


#### Vertical Spacing


## Accessibility

### ARIA

- ToggleButtonGroup has `role="group"`. You should provide an accessible label with `aria-label="label"`, `aria-labelledby="id"` or `<label>`.
- ToggleButton sets `aria-pressed="<bool>"` according to the button state. You should label each button with `aria-label`.

### Keyboard

At present, toggle buttons are in DOM order. Navigate between them with the tab key. The button behavior follows standard keyboard semantics.


# Number Field

---
productId: material-ui
title: Number field React component
components: Button, IconButton, InputLabel, FormControl, FormLabel, FormHelperText, OutlinedInput
---

# Number Field

A React component for capturing numeric input from users.


A number field is an input with increment and decrement buttons for capturing numeric input from users.

Material UI does not include a number field component out of the box, but this page provides components composed with the [Base UI `NumberField`](https://base-ui.com/react/components/number-field) and styled to align with Material Design (MD2) specifications, so they can be used with Material UI.

As such, you must install Base UI before proceeding.
The examples that follow can then be copied and pasted directly into your app.
Note that Base UI is tree-shakeable, so the final bundle will only include the components used in your project.

## Installation

<codeblock storageKey="package-manager">

```bash npm
npm install @base-ui/react
```

```bash pnpm
pnpm add @base-ui/react
```

```bash yarn
yarn add @base-ui/react
```

</codeblock>

## Usage

1. Select one of the demos below that fits your visual design needs.
2. Click **Expand code** in the toolbar.
3. Select the file that starts with `./components/`.
4. Copy the code and paste it into your project.

## Outlined field

The outlined field uses the same building-block components as Material UI's outlined `TextField`—`FormControl`, `OutlinedInput`, `InputLabel`, and `FormHelperText`—with end adornments for the increment and decrement buttons.
See [Text Field—Compononents](/material-ui/react-text-field/#components) for more details.


## Spinner field

For the spinner field component, the increment and decrement buttons are placed next to the outlined input.
This is ideal for touch devices and narrow ranges of values.


## Base UI API

See the documentation below for a complete reference to all of the props.

- [`NumberField`](https://base-ui.com/react/components/number-field#api-reference)
