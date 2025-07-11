/** @orj-module **/
import { UNBREAKABLE_ROLLBACK_CODE, UNREMOVABLE_ROLLBACK_CODE, REGEX_BOOTSTRAP_COLUMN } from '../utils/constants.js';
import {deleteText} from './deleteForward.js';
import {
    boundariesOut,
    childNodeIndex,
    CTGROUPS,
    CTYPES,
    DIRECTIONS,
    endPos,
    fillEmpty,
    getState,
    isBlock,
    isEmptyBlock,
    isUnbreakable,
    isUnremovable,
    isVisible,
    leftPos,
    rightPos,
    moveNodes,
    nodeSize,
    paragraphRelatedElements,
    prepareUpdate,
    setSelection,
    isMediaElement,
    isSelfClosingElement,
    isNotEditableNode,
    createDOMPathGenerator,
    closestElement,
    closestBlock,
    getOffsetAndCharSize,
    ZERO_WIDTH_CHARS,
    isButton,
} from '../utils/utils.js';

Text.prototype.oDeleteBackward = function (offset, alreadyMoved = false) {
    const parentElement = this.parentElement;

    if (!offset) {
        // Backspace at the beginning of a text node is not a specific case to
        // handle, let the element implementation handle it.
        parentElement.oDeleteBackward([...parentElement.childNodes].indexOf(this), alreadyMoved);
        return;
    }
    // Get the size of the unicode character to remove.
    // If the current offset split an emoji in the middle , we need to change offset to the end of the emoji
    const [newOffset, charSize] = getOffsetAndCharSize(this.nodeValue, offset, DIRECTIONS.LEFT);
    deleteText.call(this, charSize, newOffset - charSize, DIRECTIONS.LEFT, alreadyMoved);
};

const isDeletable = (node) => {
    return isMediaElement(node) || isNotEditableNode(node);
}

HTMLElement.prototype.oDeleteBackward = function (offset, alreadyMoved = false, offsetLimit) {
    const contentIsZWS = ZERO_WIDTH_CHARS.includes(this.textContent);
    let moveDest;
    if (offset) {
        const leftNode = this.childNodes[offset - 1];
        if (isUnremovable(leftNode)) {
            throw UNREMOVABLE_ROLLBACK_CODE;
        }
        if (
            isDeletable(leftNode)
        ) {
            leftNode.remove();
            return;
        }
        if (!isBlock(leftNode) || isSelfClosingElement(leftNode)) {
            /**
             * Backspace just after an inline node, convert to backspace at the
             * end of that inline node.
             *
             * E.g. <p>abc<i>def</i>[]</p> + BACKSPACE
             * <=>  <p>abc<i>def[]</i></p> + BACKSPACE
             */
            leftNode.oDeleteBackward(nodeSize(leftNode), alreadyMoved);
            return;
        }

        /**
         * Backspace just after an block node, we have to move any inline
         * content after it, up to the next block. If the cursor is between
         * two blocks, this is a theoretical case: just do nothing.
         *
         * E.g. <p>abc</p>[]de<i>f</i><p>ghi</p> + BACKSPACE
         * <=>  <p>abcde<i>f</i></p><p>ghi</p>
         */
        alreadyMoved = true;
        moveDest = endPos(leftNode);
    } else {
        if (isUnremovable(this)) {
            throw UNREMOVABLE_ROLLBACK_CODE;
        }
        // Empty unbreakable blocks should be removed with backspace, with the
        // notable exception of Bootstrap columns.
        if (isUnbreakable(this) && (REGEX_BOOTSTRAP_COLUMN.test(this.className) || !isEmptyBlock(this))) {
            throw UNBREAKABLE_ROLLBACK_CODE;
        }
        const parentEl = this.parentElement;
        // Handle editable sub-nodes
        if (
            parentEl &&
            parentEl.getAttribute("contenteditable") === "true" &&
            parentEl.oid !== "root" &&
            parentEl.parentElement &&
            !parentEl.parentElement.isContentEditable &&
            paragraphRelatedElements.includes(this.tagName) &&
            !this.previousElementSibling
        ) {
            // The first child element of a contenteditable="true" zone which
            // itself is contained in a contenteditable="false" zone can not be
            // removed if it is paragraph-like.
            throw UNREMOVABLE_ROLLBACK_CODE;
        }
        const closestLi = closestElement(this, 'li');
        if ((closestLi && !closestLi.previousElementSibling) || !isBlock(this) || isSelfClosingElement(this)) {
            /**
             * Backspace at the beginning of an inline node, nothing has to be
             * done: propagate the backspace. If the node was empty, we remove
             * it before.
             *
             * E.g. <p>abc<b></b><i>[]def</i></p> + BACKSPACE
             * <=>  <p>abc<b>[]</b><i>def</i></p> + BACKSPACE
             * <=>  <p>abc[]<i>def</i></p> + BACKSPACE
             */
            const parentOffset = childNodeIndex(this);

            if (!nodeSize(this) || contentIsZWS) {
                const visible = isVisible(this) || isButton(this);
                const restore = prepareUpdate(...boundariesOut(this));
                this.remove();
                restore();

                fillEmpty(parentEl);

                if (visible) {
                    // TODO this handle BR/IMG/etc removals../ to see if we
                    // prefer to have a dedicated handler for every possible
                    // HTML element or if we let this generic code handle it.
                    setSelection(parentEl, parentOffset);
                    return;
                }
            }
            parentEl.oDeleteBackward(parentOffset, alreadyMoved);
            return;
        }

        /** If we are at the beninning of a block node,
         *  And the previous node is empty, remove it.
         *
         *   E.g. (previousEl == empty)
         *        <p><br></p><h1>[]def</h1> + BACKSPACE
         *   <=>  <h1>[]def</h1>
         *
         *   E.g. (previousEl != empty)
         *        <h3>abc</h3><h1>[]def</h1> + BACKSPACE
         *   <=>  <h3>abc[]def</h3>
        */
        const previousElementSiblingClosestBlock = closestBlock(this.previousElementSibling);
        if (
            previousElementSiblingClosestBlock &&
            (isEmptyBlock(previousElementSiblingClosestBlock) ||
                previousElementSiblingClosestBlock.textContent === '\u200B') &&
            paragraphRelatedElements.includes(this.nodeName)
        ) {
            previousElementSiblingClosestBlock.remove();
            setSelection(this, 0);
            return;
        }

        /**
         * Backspace at the beginning of a block node. If it doesn't have a left
         * block and it is one of the special block formatting tags below then
         * convert the block into a P and return immediately. Otherwise, we have
         * to move the inline content at its beginning outside of the element
         * and propagate to the left block.
         *
         * E.g. (prev == block)
         *      <p>abc</p><div>[]def<p>ghi</p></div> + BACKSPACE
         * <=>  <p>abc</p>[]def<div><p>ghi</p></div> + BACKSPACE
         *
         * E.g. (prev != block)
         *      abc<div>[]def<p>ghi</p></div> + BACKSPACE
         * <=>  abc[]def<div><p>ghi</p></div>
         */
        if (
            !this.previousElementSibling &&
            paragraphRelatedElements.includes(this.nodeName) &&
            this.nodeName !== 'P' &&
            !closestLi
        ) {
            if (!this.textContent) {
                const p = document.createElement('p');
                p.replaceChildren(...this.childNodes);
                this.replaceWith(p);
                setSelection(p, offset);
            }
            return;
        } else {
            moveDest = leftPos(this);
        }
    }

    const domPathGenerator = createDOMPathGenerator(DIRECTIONS.LEFT, {
        leafOnly: true,
        stopTraverseFunction: isDeletable,
    });
    const domPath = domPathGenerator(this, offset)
    const leftNode = domPath.next().value;
    if (leftNode && isDeletable(leftNode)) {
        const [parent, offset] = rightPos(leftNode);
        return parent.oDeleteBackward(offset, alreadyMoved);
    }
    let node = this.childNodes[offset];
    const nextSibling = this.nextSibling;
    let currentNodeIndex = offset;

    // `offsetLimit` will ensure we never move nodes that were not initialy in
    // the element => when Deleting and merging an element the containing node
    // will temporarily be hosted in the common parent beside possible other
    // nodes. We don't want to touch those other nodes when merging two html
    // elements ex : <div>12<p>ab[]</p><p>cd</p>34</div> should never touch the
    // 12 and 34 text node.
    if (offsetLimit === undefined) {
        while (node && !isBlock(node)) {
            node = node.nextSibling;
            currentNodeIndex++;
        }
    } else {
        currentNodeIndex = offsetLimit;
    }
    let [cursorNode, cursorOffset] = moveNodes(...moveDest, this, offset, currentNodeIndex);
    setSelection(cursorNode, cursorOffset);

    // Propagate if this is still a block on the left of where the nodes were
    // moved.
    if (
        cursorNode.nodeType === Node.TEXT_NODE &&
        (cursorOffset === 0 || cursorOffset === cursorNode.length)
    ) {
        cursorOffset = childNodeIndex(cursorNode) + (cursorOffset === 0 ? 0 : 1);
        cursorNode = cursorNode.parentNode;
    }
    if (cursorNode.nodeType !== Node.TEXT_NODE) {
        const { cType } = getState(cursorNode, cursorOffset, DIRECTIONS.LEFT);
        if (cType & CTGROUPS.BLOCK && (!alreadyMoved || cType === CTYPES.BLOCK_OUTSIDE)) {
            cursorNode.oDeleteBackward(cursorOffset, alreadyMoved, cursorOffset + currentNodeIndex - offset);
        } else if (!alreadyMoved) {
            // When removing a block node adjacent to an inline node, we need to
            // ensure the block node induced line break are kept with a <br>.
            // ex : <div>a<span>b</span><p>[]c</p>d</div> => deleteBakward =>
            // <div>a<span>b</span>[]c<br>d</div> In this case we cannot simply
            // merge the <p> content into the div parent, or we would lose the
            // line break located after the <p>.
            const cursorNodeNode = cursorNode.childNodes[cursorOffset];
            const cursorNodeRightNode = cursorNodeNode ? cursorNodeNode.nextSibling : undefined;
            if (cursorNodeRightNode &&
                cursorNodeRightNode.nodeType === Node.TEXT_NODE &&
                nextSibling === cursorNodeRightNode) {
                moveDest[0].insertBefore(document.createElement('br'), cursorNodeRightNode);
            }
        }
    }
};

HTMLLIElement.prototype.oDeleteBackward = function (offset, alreadyMoved = false) {
    // If the deleteBackward is performed at the begening of a LI element,
    // we take the current LI out of the list.
    if (offset === 0) {
        this.oToggleList(offset);
        return;
    }
    // Otherwise, call the HTMLElement deleteBackward method.
    HTMLElement.prototype.oDeleteBackward.call(this, offset, alreadyMoved);
};

HTMLBRElement.prototype.oDeleteBackward = function (offset, alreadyMoved = false) {
    const parentOffset = childNodeIndex(this);
    const rightState = getState(this.parentElement, parentOffset + 1, DIRECTIONS.RIGHT).cType;
    if (rightState & CTYPES.BLOCK_INSIDE) {
        this.parentElement.oDeleteBackward(parentOffset, alreadyMoved);
    } else {
        HTMLElement.prototype.oDeleteBackward.call(this, offset, alreadyMoved);
    }
};

HTMLTableCellElement.prototype.oDeleteBackward = function (offset, alreadyMoved = false) {
    if (offset) {
        HTMLElement.prototype.oDeleteBackward.call(this, offset, alreadyMoved);
    }
};
