/*

salt-loading-spinner -- a spinner to be shown during loading

This component shows a loading spinner.

The spinner has been taken from https://loading.io/css/.

Dependencies
------------
None

Attributes
----------
period -- The period with which the spinner is spinning, in seconds. The default is 1.2.
size -- The size of the spinner, in pixels. The size is the width (and height) of the
        spinner, including a padding of 3 pixels around the actual spinner. The default
        is 80.

Custom CSS properties
---------------------
--color-spinner -- The color of the spinner. The default is white (#fff).


Usage
-----
    <salt-loading-spinner></salt-loading-spinner>

 */
class SaltLoadingSpinner extends HTMLElement {
  constructor() {
    super();

    this.attachShadow({ mode: "open" });
  }

  connectedCallback() {
    const period = this.hasAttribute("period")
      ? parseInt(this.getAttribute("period"), 10)
      : 1.2;
    const size = this.hasAttribute("size")
      ? this.getAttribute("size") + "px"
      : "80px";

    this.shadowRoot.innerHTML = `
    <style>
.lds-spinner {
  display: inline-block;
  position: relative;
  width: ${size};
  height: ${size};
}
.lds-spinner div {
  transform-origin: calc(${size} / 2) calc(${size} / 2);
  animation: lds-spinner ${(12 * period) / 11}s linear infinite;
}
.lds-spinner div:after {
  content: " ";
  display: block;
  position: absolute;
  top: 3px;
  left: calc((${size} - 6px) / 2);
  width: calc((6 / 80) * ${size});
  height: calc((18 / 80) * ${size});
  border-radius: 20%;
  background: var(--color-spinner, #fff);
}
.lds-spinner div:nth-child(1) {
  transform: rotate(0deg);
  animation-delay: ${(-11 * period) / 11}s;
}
.lds-spinner div:nth-child(2) {
  transform: rotate(30deg);
  animation-delay: ${(-10 * period) / 11}s;
}
.lds-spinner div:nth-child(3) {
  transform: rotate(60deg);
  animation-delay: ${(-9 * period) / 11}s;
}
.lds-spinner div:nth-child(4) {
  transform: rotate(90deg);
  animation-delay: ${(-8 * period) / 11}s;
}
.lds-spinner div:nth-child(5) {
  transform: rotate(120deg);
  animation-delay: ${(-7 * period) / 11}s;
}
.lds-spinner div:nth-child(6) {
  transform: rotate(150deg);
  animation-delay: ${(-6 * period) / 11}s;
}
.lds-spinner div:nth-child(7) {
  transform: rotate(180deg);
  animation-delay: ${(-5 * period) / 11}s;
}
.lds-spinner div:nth-child(8) {
  transform: rotate(210deg);
  animation-delay: ${(-4 * period) / 11}s;
}
.lds-spinner div:nth-child(9) {
  transform: rotate(240deg);
  animation-delay: ${(-3 * period) / 11}s;
}
.lds-spinner div:nth-child(10) {
  transform: rotate(270deg);
  animation-delay: ${(-2 * period) / 11}s;
}
.lds-spinner div:nth-child(11) {
  transform: rotate(300deg);
  animation-delay: ${(-1 * period) / 11}s;
}
.lds-spinner div:nth-child(12) {
  transform: rotate(330deg);
  animation-delay: 0s;
}
@keyframes lds-spinner {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
    
    </style>
    <!-- taken from https://loading.io/css/ -->
    <div class="lds-spinner"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div>
    `;
  }
}

if (!customElements.get("salt-loading-spinner")) {
  customElements.define("salt-loading-spinner", SaltLoadingSpinner);
}
