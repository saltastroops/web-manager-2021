/*

salt-block-view -- Custom element for viewing block content.

The block view displays a block, which is requested as HTML from the server. It includes
navigation elements for stepping through the blocks.

Dependencies
------------
The salt-loading-overlay component is used by this component.

Attributes
----------
proposal-code: The proposal code of the proposal whose blocks are viewed.
block-codes: The comma-separated list of block codes.

Usage
-----
    <salt-block-view
            proposal-code="{{ proposal_code }}"
            block-codes="{{ block_codes | join(',') }}">
    </salt-block-view>

Methods
-------
set_block_code(block_code) -- Change the block code.

 */

class SaltBlockView extends HTMLElement {
  constructor() {
    super();
  }

  /**
   * Initialise the component and fetch the initial block.
   */
  connectedCallback() {
    this.proposalCode = this.getAttribute("proposal-code");
    this.blockCodes = this.getAttribute("block-codes").split(/\s*,\s*/);
    this.blockContent = null;
    this.loading = false;
    this.error = null;

    // initialise the block code index
    this.currentBlockCodeIndex = 0;
    if (this.hasAttribute("initial-block-code")) {
      const initialBlockCode = this.getAttribute("initial-block-code");
      this.currentBlockCodeIndex = this.blockCodes.indexOf(initialBlockCode);
      if (this.currentBlockCodeIndex === -1) {
        throw new Error(
          `The initial block code (${initialBlockCode}) is not in the list of block codes passed via the block-codes attribute.`
        );
      }
    }

    // non-block content
    const navigationContent = `
        <nav class="block-view__nav">
            <button class="block-view__previous button button--normal-action">Prev</button>
            <select class="block_view__select select">
              ${this.blockCodes
                .map(
                  (code, index) =>
                    `<option value="${index}" ${
                      index === this.currentBlockCodeIndex
                        ? 'selected="selected"'
                        : ""
                    }>${code}</option>`
                )
                .join("")}
            </select>
            <button class="block-view__next button button--normal-action">Next</button>
        </nav>
    `;
    this.innerHTML = `
    <style>
    .block-view__main {
      min-height: 200px;
      min-width: 200px;
      position: relative;
    }
    
    .block-view__loading-overlay {
      height: 100%;
      left: 0;
      position: absolute;
      top: 0;
      width: 100%;
      z-index: 100;
    }
    
    .block_view__loading-spinner {
      left: calc(50% - 40px);
      position: absolute;
      top: calc(50% - 40px);
    }
    </style>
    <div class="block-view">
        ${navigationContent}
        <div class="notification notification--error" style="display: none">Something's wrong: ${this.error}</div>
        <div class="block-view__main">
            <div class="block-view__content">
            ${this.blockContent}
            </div>
            <div class="block-view__loading-overlay loading-overlay" style="display: none">
                <salt-loading-spinner class="block_view__loading-spinner"></salt-loading-spinner>
            </div>
        </div>
        ${navigationContent}
    </div>
    `;

    // add the navigation listeners
    this.onPreviousButtonClickListener = this.onPreviousButtonClick.bind(this);
    this.onSelectChangeListener = this.onSelectChange.bind(this);
    this.onNextButtonClickListener = this.onNextButtonClick.bind(this);
    this.querySelectorAll(".block-view__previous").forEach((e) => {
      e.addEventListener("click", this.onPreviousButtonClickListener);
    });
    this.querySelectorAll(".block_view__select").forEach((e) => {
      e.addEventListener("change", this.onSelectChangeListener);
    });
    this.querySelectorAll(".block-view__next").forEach((e) => {
      e.addEventListener("click", this.onNextButtonClickListener);
    });

    // initial rendering
    this.render();

    // fetch the initial block content
    if (this.blockCodes.length === 0) {
      throw new Error("The list of block codes is empty.");
    }
    this.fetchBlock(this.blockCodes[this.currentBlockCodeIndex]);
  }

  /**
   * Clean up.
   */
  disconnectedCallback() {
    // cancel the block query (if there is one)
    if (this.fetchController) {
      this.fetchController.abort();
    }

    // remove all listeners
    this.querySelectorAll(".block-view__previous").forEach((e) => {
      e.removeEventListener("click", this.onPreviousButtonClickListener);
    });
    this.querySelectorAll(".block-view__select").forEach((e) => {
      e.removeEventListener("change", this.onSelectChangeListener);
    });
    this.querySelectorAll(".block-view__next").forEach((e) => {
      e.removeEventListener("click", this.onNextButtonClickListener);
    });
  }

  /**
   * Event handler for buttons for moving to the previous block.
   */
  onPreviousButtonClick() {
    // load the the previous block
    this.currentBlockCodeIndex--;
    const blockCode = this.blockCodes[this.currentBlockCodeIndex];
    this.fetchBlock(blockCode);
  }

  /**
   * Event handler for select menus for choosing a block.
   */
  onSelectChange(e) {
    // load the selected block
    this.currentBlockCodeIndex = e.target.value;
    const blockCode = this.blockCodes[this.currentBlockCodeIndex];
    this.fetchBlock(blockCode);
  }

  /**
   * Event handler for buttons for moving to the next block.
   */
  onNextButtonClick() {
    // load the the next block
    this.currentBlockCodeIndex++;
    const blockCode = this.blockCodes[this.currentBlockCodeIndex];
    this.fetchBlock(blockCode);
  }

  /**
   * Render the element.
   */
  render() {
    // render the block content
    this.querySelector(".block-view__content").innerHTML = this.blockContent;

    // show or hide the error message element
    const errorNotification = this.querySelector(".notification--error");
    if (this.error) {
      errorNotification.style.display = "block";
    } else {
      errorNotification.style.display = "none";
    }

    // show or hide the loading overlay
    const loadingOverlay = this.querySelector(".block-view__loading-overlay");
    if (this.loading) {
      loadingOverlay.style.display = "block";
    } else {
      loadingOverlay.style.display = "none";
    }

    // update the disabled status of the navigation buttons
    if (!this.loading) {
      this.updatePreviousButtons();
      this.updateNextButtons();
    } else {
      this.querySelectorAll(".block-view__nav button").forEach((e) => {
        e.setAttribute("disabled", "disabled");
      });
    }

    // update the select menus
    this.updateSelectMenus();
  }

  /**
   * Fetch block content.
   */
  fetchBlock(blockCode) {
    if (this.fetchController) {
      this.fetchController.abort();
    }
    this.fetchController = new AbortController();
    const { signal } = this.fetchController;
    this.error = null;
    this.loading = true;
    this.blockContent = null;
    this.render();
    let ok = true;
    fetch(`/api/proposals/${this.proposalCode}/blocks/${blockCode}`, { signal })
      .then((resp) => {
        ok = resp.ok;
        return resp.json();
      })
      .then((data) => {
        if (!ok) throw new Error(data.detail);
        this.blockContent = data.html;
        this.loading = false;
        this.render();
      })
      .catch((error) => {
        if (error.name === "AbortError") {
          return; // the fetch has been aborted; there is nothing to do
        }
        this.error = error.message;
        this.loading = false;
        this.render();
      });
  }

  updatePreviousButtons() {
    if (this.currentBlockCodeIndex < 1 || this.loading) {
      this.querySelectorAll(".block-view__previous").forEach((e) => {
        e.setAttribute("disabled", "disabled");
      });
    } else {
      this.querySelectorAll(".block-view__previous").forEach((e) => {
        e.removeAttribute("disabled");
      });
    }
  }

  updateNextButtons() {
    if (
      this.currentBlockCodeIndex >= this.blockCodes.length - 1 ||
      this.loading
    ) {
      this.querySelectorAll(".block-view__next").forEach((e) => {
        e.setAttribute("disabled", "disabled");
      });
    } else {
      this.querySelectorAll(".block-view__next").forEach((e) => {
        e.removeAttribute("disabled");
      });
    }
  }

  updateSelectMenus() {
    this.querySelectorAll(".block_view__select").forEach((e) => {
      e.value = this.currentBlockCodeIndex;
    });
  }
}

if (!customElements.get("salt-block-view")) {
  customElements.define("salt-block-view", SaltBlockView);
}
