# Web Components

The Web Manager makes use of various web components. These are written in vanilla JavaScript, but may require recent browser versions. No attempt has been made to support, say, Internet Explorer.

## salt-loading-spinner

### Dependencies

There is no dependency on any other web components.

### Description

The `salt-loading-spinner` component is a rotating spinner, which is intended to indicate a loading status. The rotation period and size of the spinner can be set with attributes.

| Attribute | Description                                                                                                           | Required | Default | Example |
| --------- | --------------------------------------------------------------------------------------------------------------------- | -------- | ------- | ------- |
| period    | The rotation period of the spinner, in seconds.                                                                       | No       | 1.2     | 2.4     |
| size      | The size (i.e. width and height) of the spinner, in pixels. This includes a little bit of padding around the spinner. | No       | 80      | 40      |

!!! warning
Currently the spinner looks a bit odd if you use a size other than the default 80 pixels.

The component does not listen to attribute changes. You can change the colour of the spinner by means of a custom property.

| Custom property | Description         | Example |
| --------------- | ------------------- | ------- |
| --color-spinner | The spinner colour. | #ffffff |

The spinner has been adapted from a spinner on [https://loading.io/css/](https://loading.io/css/).

## salt-block-view

### Dependencies

The `salt-loading-spinner` web component must be available.

### Description

The `salt-block-view` component lets the user view indiviual blocks of a proposal. It includes navigation elements for moving to the previous or next button, as well as a select menu for directly choosing a block.

The component takes the following attributes.

| Attribute          | Description                                                                                                                                | Required | Default                                   | Example                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ----------------------------------------- | -------------------------------------------- |
| block-codes        | A comma-separated list of block codes. All the blocks in this list must belong to the proposal specified by the `proposal-code` attribute. | Yes      | n/a                                       | xfg53koluy67hj, ffacreuki5t6g, e1klsdiv7093g |
| initial-block-code | The block code of the block to show initially.                                                                                             | No       | The first item in the list of block codes | ffacreuki5t6g                                |
| proposal-code      | The proposal code of the blocks viewed.                                                                                                    | Yes      | n/a                                       | 2020-2-SCI-042                               |

The component does not listen to attribute changes. By default the component initially loads the first block of the supplied list of block codes. However, you can change this by explicitly passing in the initial block to display by means of the `initial-block-code` attribute.
