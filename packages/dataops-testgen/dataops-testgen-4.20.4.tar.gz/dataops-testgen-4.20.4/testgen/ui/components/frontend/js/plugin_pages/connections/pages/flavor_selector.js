/**
 * @import { Flavor } from '../../../components/connection_form.js';
 * 
 * @typedef Properties
 * @type {object}
 * @property {Array.<Flavor>} flavors
 * @property {number?} selected
 * @property {(number|null)} columns
 * @property {((idx: number, a: Flavor?) => void)?} onChange
 */

import van from '../../../van.min.js';
import { getValue, loadStylesheet } from '../../../utils.js';

const rowGap = 16;
const columnSize = '200px';
const { div, span, img, h3 } = van.tags;

const DatabaseFlavorSelector = (/** @type Properties */props) => {
    loadStylesheet('databaseFlavorSelector', stylesheet);

    const flavors = getValue(props.flavors);
    const numberOfColumns = getValue(props.columns) ?? 3;
    const initialSelection = getValue(props.selected);
    const selectedIdx = van.state(initialSelection);

    van.derive(() => {
        const selectedFlavor = flavors[selectedIdx.val];
        if (selectedFlavor) {
            props.onChange?.(selectedIdx.val, selectedFlavor);
        }
    });

    return div(
        {class: 'tg-flavor-selector-page'},
        h3(
            {class: 'tg-flavor-selector-header'},
            'Select your database type'
        ),
        div(
            {
                class: 'tg-flavor-selector',
                style: `grid-template-columns: ${Array(numberOfColumns).fill(columnSize).join(' ')}; row-gap: ${rowGap}px;`
            },
            flavors.map((flavor, idx) =>
                DatabaseFlavor(
                    idx,
                    flavor,
                    selectedIdx,
                    () => selectedIdx.val = idx,
                )
            ),
        )
    );
};

const DatabaseFlavor = (
    /** @type number */ idx,
    /** @type Falvor */ props,
    /** @type number */ selection,
    /** @type Function */ onClick,
) => {
    const cssClass = van.derive(() => `tg-flavor ${getValue(selection) === getValue(idx) ? 'selected' : ''}`);
    return div(
        {
            class: cssClass,
            onclick: onClick,
        },
        span({class: 'tg-flavor-focus-state-indicator'}, ''),
        img(
            {class: 'tg-flavor--icon', src: props.icon},
        ),
        span(
            {class: 'tg-flavor--label'},
            props.label
        ),
    );
};

const stylesheet = new CSSStyleSheet();
stylesheet.replace(`
    .tg-flavor-selector-header {
        margin: unset;
        margin-bottom: 16px;
        font-weight: 400;
    }

    .tg-flavor-selector {
        display: grid;
        grid-template-rows: auto;
        column-gap: 32px;
    }

    .tg-flavor {
        display: flex;
        align-items: center;
        padding: 16px;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        cursor: pointer;
        position: relative;
    }

    .tg-flavor .tg-flavor-focus-state-indicator::before {
        content: "";
        opacity: 0;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        position: absolute;
        pointer-events: none;
        border-radius: inherit;
        background: var(--button-primary-hover-state-background);
    }

    .tg-flavor.selected {
        border-color: var(--primary-color);
    }

    .tg-flavor:hover .tg-flavor-focus-state-indicator::before,
    .tg-flavor.selected .tg-flavor-focus-state-indicator::before {
        opacity: var(--button-hover-state-opacity);
    }

    .tg-flavor--icon {
        margin-right: 16px;
    }

    .tg-flavor--label {
        font-weight: 500;
    }
`);

export { DatabaseFlavorSelector };
