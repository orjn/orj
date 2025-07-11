/** @orj-module */

import { OrjEditor, parseHTML, setSelection, insertCharsAt } from '../../src/OrjEditor.js';
import {
    parseMultipleTextualSelection,
    redo,
    setTestSelection,
    targetDeepest,
    undo,
    patchEditorIframe,
    unformat,
} from '../utils.js';
import { Deferred } from "@web/core/utils/concurrency";

const applyConcurentActions = (clientInfos, concurentActions) => {
    const clientInfosList = Object.values(clientInfos);
    for (const clientInfo of clientInfosList) {
        if (typeof concurentActions[clientInfo.clientId] === 'function') {
            concurentActions[clientInfo.clientId](clientInfo.editor);
        }
    }
};

const mergeClientsSteps = clientInfos => {
    const clientInfosList = Object.values(clientInfos);
    for (const clientInfoA of clientInfosList) {
        for (const clientInfoB of clientInfosList) {
            if (clientInfoA === clientInfoB) {
                continue;
            }
            for (const step of clientInfoB.recordedHistorySteps) {
                clientInfoA.editor.onExternalHistorySteps([JSON.parse(JSON.stringify(step))]);
            }
        }
    }
};

const testSameHistory = clientInfos => {
    const clientInfosList = Object.values(clientInfos);

    const firstClientInfo = clientInfosList[0];
    const historyLength = firstClientInfo.editor._historySteps.length;

    for (const clientInfo of clientInfosList.slice(1)) {
        window.chai
            .expect(firstClientInfo.editor._historySteps.length)
            .to.be.equal(historyLength, 'The history size should be the same.');
        for (let i = 0; i < historyLength; i++) {
            try {
                window.chai
                    .expect(firstClientInfo.editor._historySteps[i].id)
                    .to.be.equal(
                    clientInfo.editor._historySteps[i].id,
                    `History steps are not consistent accross clients.`,
                );
            } catch (e) {
                console.log(
                    'Clients steps:',
                    clientInfosList.map(x => x.editor._historySteps.map(y => `${y.id}`)),
                );
                throw e;
            }
        }
    }
};

const testMultiEditor = async spec => {
    const clientInfos = {};
    const concurentActions = spec.concurentActions || [];
    const clientIds = spec.clientIds || Object.keys(concurentActions);
    for (const clientId of clientIds) {
        clientInfos[clientId] = {
            clientId,
            recordedHistorySteps: [],
        };
        const clientInfo = clientInfos[clientId];
        clientInfo.iframe = document.createElement('iframe');
        if (navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
            // Firefox reset the page without this hack.
            // With this hack, chrome does not render content.
            clientInfo.iframe.setAttribute('src', ' javascript:void(0);');
        }
        document.body.appendChild(clientInfo.iframe);
        patchEditorIframe(clientInfo.iframe);

        clientInfo.editable = document.createElement('div');
        clientInfo.editable.setAttribute('contenteditable', 'true');
        clientInfo.editable.innerHTML = spec.contentBefore;
    }
    const clientInfosList = Object.values(clientInfos);

    let shouldListenSteps = false;

    // Init the editors
    for (const clientInfo of clientInfosList) {
        const selections = parseMultipleTextualSelection(clientInfo.editable);
        const iframeWindow = clientInfo.iframe.contentWindow;
        const iframeDocument = iframeWindow.document;
        iframeDocument.body.appendChild(clientInfo.editable);

        // Insure all the client will have the same starting id.
        let nextId = 1;
        OrjEditor.prototype._generateId = () => 'fake_id_' + nextId++;

        clientInfo.editor = new OrjEditor(clientInfo.editable, Object.assign({
            toSanitize: false,
            document: iframeDocument,
            collaborationClientId: clientInfo.clientId,
            onHistoryStep: step => {
                if (shouldListenSteps) {
                    clientInfo.recordedHistorySteps.push(step);
                }
            },
            onHistoryMissingParentSteps: ({ step, fromStepId }) => {
                const missingSteps = clientInfos[step.clientId].editor.historyGetMissingSteps({
                    fromStepId,
                    toStepId: step.id,
                });
                if (missingSteps === -1 || !missingSteps.length) {
                    throw new Error('Impossible to get the missing steps.');
                }
                clientInfo.editor.onExternalHistorySteps(missingSteps.concat([step]));
            },
        }, spec.options || {}));
        clientInfo.editor.keyboardType = 'PHYSICAL';
        const selection = selections[clientInfo.clientId];
        if (selection) {
            setTestSelection(selection, iframeDocument);
        } else {
            iframeDocument.getSelection().removeAllRanges();
        }
        // Flush the history so that steps generated by the parsing of the
        // selection and the editor loading are not recorded.
        clientInfo.editor.observerFlush();
    }

    shouldListenSteps = true;

    // From now, any any step from a client must have a different ID.
    let concurentNextId = 1;
    OrjEditor.prototype._generateId = () => 'fake_concurent_id_' + concurentNextId++;

    if (spec.afterCreate) {
        await spec.afterCreate(clientInfos);
    }

    shouldListenSteps = false;

    // Render textual selection.

    const cursorNodes = {};
    for (const clientInfo of clientInfosList) {
        const iframeDocument = clientInfo.iframe.contentWindow.document;
        const clientSelection = iframeDocument.getSelection();
        if (clientSelection.anchorNode === null) {
            continue;
        }

        const [anchorNode, anchorOffset] = targetDeepest(
            clientSelection.anchorNode,
            clientSelection.anchorOffset,
        );
        const [focusNode, focusOffset] = targetDeepest(
            clientSelection.focusNode,
            clientSelection.focusOffset,
        );

        const clientId = clientInfo.clientId;
        cursorNodes[focusNode.oid] = cursorNodes[focusNode.oid] || [];
        cursorNodes[focusNode.oid].push({ type: 'focus', clientId, offset: focusOffset });
        cursorNodes[anchorNode.oid] = cursorNodes[anchorNode.oid] || [];
        cursorNodes[anchorNode.oid].push({ type: 'anchor', clientId, offset: anchorOffset });
    }

    for (const nodeOid of Object.keys(cursorNodes)) {
        cursorNodes[nodeOid] = cursorNodes[nodeOid].sort((a, b) => {
            return b.offset - a.offset || b.clientId.localeCompare(a.clientId);
        });
    }

    for (const clientInfo of clientInfosList) {
        clientInfo.editor.observerUnactive();
        for (const [nodeOid, cursorsData] of Object.entries(cursorNodes)) {
            const node = clientInfo.editor.idFind(nodeOid);
            for (const cursorData of cursorsData) {
                const cursorString =
                    cursorData.type === 'anchor'
                        ? `[${cursorData.clientId}}`
                        : `{${cursorData.clientId}]`;
                insertCharsAt(cursorString, node, cursorData.offset);
            }
        }
    }

    if (spec.contentAfter) {
        for (const clientInfo of clientInfosList) {
            const value = clientInfo.editable.innerHTML;
            window.chai
                .expect(value)
                .to.be.equal(spec.contentAfter, `error with client ${clientInfo.clientId}`);
        }
    }
    if (spec.afterCursorInserted) {
        await spec.afterCursorInserted(clientInfos);
    }
    for (const clientInfo of clientInfosList) {
        clientInfo.editor.destroy();
        clientInfo.iframe.remove();
    }
};

describe('Collaboration', () => {
    describe('Conflict resolution', () => {
        it('all client steps should be on the same order', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2', 'c3'],
                contentBefore: '<p><x>a[c1}{c1]</x><y>e[c2}{c2]</y><z>i[c3}{c3]</z></p>',
                afterCreate: clientInfos => {
                    applyConcurentActions(clientInfos, {
                        c1: editor => {
                            editor.execCommand('insert', 'b');
                            editor.execCommand('insert', 'c');
                            editor.execCommand('insert', 'd');
                        },
                        c2: editor => {
                            editor.execCommand('insert', 'f');
                            editor.execCommand('insert', 'g');
                            editor.execCommand('insert', 'h');
                        },
                        c3: editor => {
                            editor.execCommand('insert', 'j');
                            editor.execCommand('insert', 'k');
                            editor.execCommand('insert', 'l');
                        },
                    });
                    mergeClientsSteps(clientInfos);
                    testSameHistory(clientInfos);
                },
                contentAfter: '<p><x>abcd[c1}{c1]</x><y>efgh[c2}{c2]</y><z>ijkl[c3}{c3]</z></p>',
            });
        });
        it('should 2 client insertText in 2 different paragraph', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>ab[c1}{c1]</p><p>cd[c2}{c2]</p>',
                afterCreate: clientInfos => {
                    applyConcurentActions(clientInfos, {
                        c1: editor => {
                            editor.execCommand('insert', 'e');
                        },
                        c2: editor => {
                            editor.execCommand('insert', 'f');
                        },
                    });
                    mergeClientsSteps(clientInfos);
                    testSameHistory(clientInfos);
                },
                contentAfter: '<p>abe[c1}{c1]</p><p>cdf[c2}{c2]</p>',
            });
        });
        it('should 2 client insertText twice in 2 different paragraph', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>ab[c1}{c1]</p><p>cd[c2}{c2]</p>',
                afterCreate: clientInfos => {
                    applyConcurentActions(clientInfos, {
                        c1: editor => {
                            editor.execCommand('insert', 'e');
                            editor.execCommand('insert', 'f');
                        },
                        c2: editor => {
                            editor.execCommand('insert', 'g');
                            editor.execCommand('insert', 'h');
                        },
                    });
                    mergeClientsSteps(clientInfos);
                    testSameHistory(clientInfos);
                },
                contentAfter: '<p>abef[c1}{c1]</p><p>cdgh[c2}{c2]</p>',
            });
        });
        it('should insertText with client 1 and deleteBackward with client 2', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>ab[c1}{c1][c2}{c2]c</p>',
                afterCreate: clientInfos => {
                    applyConcurentActions(clientInfos, {
                        c1: editor => {
                            editor.execCommand('insert', 'd');
                        },
                        c2: editor => {
                            editor.execCommand('oDeleteBackward');
                        },
                    });
                    mergeClientsSteps(clientInfos);
                    testSameHistory(clientInfos);
                },
                contentAfter: '<p>a[c2}{c2]c[c1}{c1]dc</p>',
            });
        });
        it('should insertText twice with client 1 and deleteBackward twice with client 2', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>ab[c1}{c1][c2}{c2]c</p>',
                afterCreate: clientInfos => {
                    applyConcurentActions(clientInfos, {
                        c1: editor => {
                            editor.execCommand('insert', 'd');
                            editor.execCommand('insert', 'e');
                        },
                        c2: editor => {
                            editor.execCommand('oDeleteBackward');
                            editor.execCommand('oDeleteBackward');
                        },
                    });
                    mergeClientsSteps(clientInfos);
                    testSameHistory(clientInfos);
                },
                contentAfter: '<p>[c2}{c2]cd[c1}{c1]ec</p>',
            });
        });
    });
    it('should reset from snapshot', async () => {
        await testMultiEditor({
            clientIds: ['c1', 'c2'],
            contentBefore: '<p>a[c1}{c1]</p>',
            afterCreate: clientInfos => {
                clientInfos.c1.editor.execCommand('insert', 'b');
                clientInfos.c1.editor._historyMakeSnapshot();
                // Insure the snapshot is considered to be older than 30 seconds.
                clientInfos.c1.editor._historySnapshots[0].time = 1;
                const { steps } = clientInfos.c1.editor.historyGetSnapshotSteps();
                clientInfos.c2.editor.historyResetFromSteps(steps);

                chai.expect(clientInfos.c2.editor._historySteps.map(x => x.id)).to.deep.equal([
                    'fake_concurent_id_2',
                ]);
                chai.expect(
                    clientInfos.c2.editor._historySteps[0].mutations.map(x => x.id),
                ).to.deep.equal(['fake_id_1']);
            },
            contentAfter: '<p>ab[c1}{c1]</p>',
        });
    });
    describe('steps whith no parent in history', () => {
        it('should be able to retreive steps when disconnected from clients that has send step', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2', 'c3'],
                contentBefore: '<p><x>a[c1}{c1]</x><y>b[c2}{c2]</y><z>c[c3}{c3]</z></p>',
                afterCreate: clientInfos => {
                    clientInfos.c1.editor.execCommand('insert', 'd');
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);
                    clientInfos.c2.editor.execCommand('insert', 'e');
                    clientInfos.c1.editor.onExternalHistorySteps([
                        clientInfos.c2.editor._historySteps[2],
                    ]);
                    clientInfos.c3.editor.onExternalHistorySteps([
                        clientInfos.c2.editor._historySteps[2],
                    ]);
                    // receive step 1 after step 2
                    clientInfos.c3.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);
                    testSameHistory(clientInfos);
                },
                contentAfter: '<p><x>ad[c1}{c1]</x><y>be[c2}{c2]</y><z>c[c3}{c3]</z></p>',
            });
        });
        it('should receive steps where parent was not received', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2', 'c3'],
                contentBefore: '<p><i>a[c1}{c1]</i><b>b[c2}{c2]</b></p>',
                afterCreate: clientInfos => {
                    clientInfos.c1.editor.execCommand('insert', 'c');
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);

                    // Client 3 connect firt to client 1 that made a snapshot.

                    clientInfos.c1.editor._historyMakeSnapshot();
                    // Fake the time of the snapshot so it is considered to be
                    // older than 30 seconds.
                    clientInfos.c1.editor._historySnapshots[0].time = 1;
                    const { steps } = clientInfos.c1.editor.historyGetSnapshotSteps();
                    clientInfos.c3.editor.historyResetFromSteps(steps);

                    // In the meantime client 2 send the step to client 1
                    clientInfos.c2.editor.execCommand('insert', 'd');
                    clientInfos.c2.editor.execCommand('insert', 'e');
                    clientInfos.c1.editor.onExternalHistorySteps([
                        clientInfos.c2.editor._historySteps[2],
                    ]);
                    clientInfos.c1.editor.onExternalHistorySteps([
                        clientInfos.c2.editor._historySteps[3],
                    ]);

                    // Now client 2 is connected to client 3 and client 2 make a new step.
                    clientInfos.c2.editor.execCommand('insert', 'f');
                    clientInfos.c1.editor.onExternalHistorySteps([
                        clientInfos.c2.editor._historySteps[4],
                    ]);
                    clientInfos.c3.editor.onExternalHistorySteps([
                        clientInfos.c2.editor._historySteps[4],
                    ]);
                },
                contentAfter: '<p><i>ac[c1}{c1]</i><b>bdef[c2}{c2]</b></p>',
            });
        });
    });
    describe('sanitize', () => {
        it('should sanitize when adding a node', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p><x>a</x></p>',
                afterCreate: clientInfos => {
                    const script = document.createElement('script');
                    script.innerHTML = 'console.log("xss")';
                    clientInfos.c1.editable.append(script);
                    clientInfos.c1.editor.historyStep();
                    window.chai.expect(clientInfos.c1.editor._historySteps[1]).is.not.undefined;
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);
                    window.chai
                        .expect(clientInfos.c2.editor.editable.innerHTML)
                        .to.equal('<p><x>a</x></p>');
                },
            });
        });
        it('should sanitize when adding a script as descendant', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>a[c1}{c1][c2}{c2]</p>',
                afterCreate: clientInfos => {
                    const i = document.createElement('i');
                    i.innerHTML = '<b>b</b><script>alert("c");</script>';
                    clientInfos.c1.editable.appendChild(i);
                    clientInfos.c1.editor.historyStep();
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);
                },
                afterCursorInserted: clientInfos => {
                    chai.expect(clientInfos.c2.editable.innerHTML).to.equal(
                        '<p>a[c1}{c1][c2}{c2]</p><i><b>b</b></i>',
                    );
                },
            });
        });
        it('should sanitize when changing an attribute', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>a<img></p>',
                afterCreate: clientInfos => {
                    const img = clientInfos.c1.editable.childNodes[0].childNodes[1];
                    img.setAttribute('class', 'b');
                    img.setAttribute('onerror', 'console.log("xss")');
                    clientInfos.c1.editor.historyStep();
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);
                    window.chai
                        .expect(clientInfos.c1.editor.editable.innerHTML)
                        .to.equal('<p>a<img class="b" onerror="console.log(&quot;xss&quot;)"></p>');
                    window.chai
                        .expect(clientInfos.c2.editor.editable.innerHTML)
                        .to.equal('<p>a<img class="b"></p>');
                },
            });
        });

        it('should sanitize when undo is adding a script node', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>a</p>',
                afterCreate: clientInfos => {
                    const script = document.createElement('script');
                    script.innerHTML = 'console.log("xss")';
                    clientInfos.c1.editable.append(script);
                    clientInfos.c1.editor.historyStep();
                    script.remove();
                    clientInfos.c1.editor.historyStep();
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);
                    // Change the client in order to be undone from client 2
                    clientInfos.c1.editor._historySteps[2].clientId = 'c2';
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[2],
                    ]);
                    clientInfos.c2.editor.historyUndo();
                    window.chai
                        .expect(clientInfos.c2.editor.editable.innerHTML)
                        .to.equal('<p>a</p>');
                },
            });
        });
        it('should sanitize when undo is adding a descendant script node', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>a</p>',
                afterCreate: clientInfos => {
                    const div = document.createElement('div');
                    div.innerHTML = '<i>b</i><script>console.log("xss")</script>';
                    clientInfos.c1.editable.append(div);
                    clientInfos.c1.editor.historyStep();
                    div.remove();
                    clientInfos.c1.editor.historyStep();
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);
                    // Change the client in order to be undone from client 2
                    clientInfos.c1.editor._historySteps[2].clientId = 'c2';
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[2],
                    ]);
                    clientInfos.c2.editor.historyUndo();
                    window.chai
                        .expect(clientInfos.c2.editor.editable.innerHTML)
                        .to.equal('<p>a</p><div><i>b</i></div>');
                },
            });
        });
        it('should sanitize when undo is changing an attribute', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>a<img></p>',
                afterCreate: clientInfos => {
                    const img = clientInfos.c1.editable.childNodes[0].childNodes[1];
                    img.setAttribute('class', 'b');
                    img.setAttribute('onerror', 'console.log("xss")');
                    clientInfos.c1.editor.historyStep();
                    img.setAttribute('class', '');
                    img.setAttribute('onerror', '');
                    clientInfos.c1.editor.historyStep();
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[1],
                    ]);
                    // Change the client in order to be undone from client 2
                    clientInfos.c1.editor._historySteps[2].clientId = 'c2';
                    clientInfos.c2.editor.onExternalHistorySteps([
                        clientInfos.c1.editor._historySteps[2],
                    ]);
                    clientInfos.c2.editor.historyUndo();
                    window.chai
                        .expect(clientInfos.c2.editor.editable.innerHTML)
                        .to.equal('<p>a<img class="b"></p>');
                },
            });
        });
        it('should not sanitize contenteditable attribute (check DOMPurify DEFAULT_ALLOWED_ATTR)', async () => {
            await testMultiEditor({
                clientIds: ['c1'],
                contentBefore: '<div class="remove-me" contenteditable="true">[c1}{c1]<br></div>',
                afterCreate: clientInfos => {
                    const editor = clientInfos.c1.editor;
                    const target = editor.editable.querySelector('.remove-me');
                    target.classList.remove("remove-me");
                    editor.historyStep();
                    undo(editor);
                    redo(editor);
                },
                contentAfter: '<div contenteditable="true">[c1}{c1]<br></div>',
            });
        });
        it("should not sanitize the content of an element recursively when sanitizing an attribute", async () => {
            await testMultiEditor({
                clientIds: ["c1", "c2"],
                contentBefore: "<div class='content' data-oe-protected='true'><p>base</p></div>",
                afterCreate: (clientInfos) => {
                    const editor1 = clientInfos.c1.editor;
                    const editor2 = clientInfos.c2.editor;
                    const content1 = editor1.editable.querySelector(".content");
                    const content2 = editor2.editable.querySelector(".content");
                    content2.append(
                        ...parseHTML(
                            editor2.document,
                            "<p>mysecretcode</p><script>secretStuff?.();</script>"
                        ).children
                    );
                    editor2.editable.append(
                        ...parseHTML(editor2.document, "<p>sanitycheckc2</p>").children
                    );
                    editor2.historyStep();
                    content1.setAttribute("onclick", "javascript:badStuff?.()");
                    content1.setAttribute("data-info", "43");
                    editor1.editable.prepend(
                        ...parseHTML(editor1.document, "<p>sanitycheckc1</p>").children
                    );
                    editor1.historyStep();
                    mergeClientsSteps(clientInfos);
                    // client 1:
                    // did not receive the secret code doing secret stuff from client 2 because
                    // it was protected
                    // still has its own onclick attribute doing bad stuff, because he wrote it
                    // himself
                    window.chai.expect(clientInfos.c1.editor.editable.innerHTML).to.equal(
                        unformat(`
                            <p>sanitycheckc1</p>
                            <div class="content" data-oe-protected="true" onclick="javascript:badStuff?.()" data-info="43">
                                <p>base</p>
                            </div>
                            <p>sanitycheckc2</p>
                        `)
                    );
                    // client 2:
                    // did not receive the onclick attribute doing bad stuff from client 1 (was
                    // sanitized)
                    // received the `data-info="43"` from client 1, and doing so did not sanitize
                    // the custom script doing secret stuff
                    window.chai.expect(clientInfos.c2.editor.editable.innerHTML).to.equal(
                        unformat(`
                            <p>sanitycheckc1</p>
                            <div class="content" data-oe-protected="true" data-info="43">
                                <p>base</p>
                                <p>mysecretcode</p>
                                <script>secretStuff?.();</script>
                            </div>
                            <p>sanitycheckc2</p>
                        `)
                    );
                },
            });
        });
    });
    describe('data-oe-protected', () => {
        it('should not share protected mutations and share unprotected ones', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>[c1}{c1][c2}{c2]</p>',
                afterCreate: clientInfos => {
                    clientInfos.c1.editor.editable.prepend(...parseHTML(clientInfos.c1.editor.document, unformat(`
                        <div data-oe-protected="true">
                            <p id="true"><br></p>
                            <div data-oe-protected="false">
                                <p id="false"><br></p>
                            </div>
                        </div>
                    `)).children);
                    clientInfos.c1.editor.historyStep();
                    const pTrue = clientInfos.c1.editor.editable.querySelector('#true');
                    setSelection(pTrue, 0);
                    pTrue.prepend(clientInfos.c1.editor.document.createTextNode('a'));
                    clientInfos.c1.editor.historyStep();
                    const pFalse = clientInfos.c1.editor.editable.querySelector('#false');
                    setSelection(pFalse, 0);
                    clientInfos.c1.editor.execCommand('insert', 'a');
                    clientInfos.c2.editor.onExternalHistorySteps(clientInfos.c1.editor._historySteps);
                    testSameHistory(clientInfos);
                },
                afterCursorInserted:  clientInfos => {
                    chai.expect(clientInfos.c1.editable.innerHTML).to.equal(unformat(`
                        <div data-oe-protected="true">
                            <p id="true">a<br></p>
                            <div data-oe-protected="false">
                                <p id="false">a[c1}{c1]</p>
                            </div>
                        </div>
                        <p>[c2}{c2]</p>
                    `));
                    chai.expect(clientInfos.c2.editable.innerHTML).to.equal(unformat(`
                        <div data-oe-protected="true">
                            <p id="true"><br></p>
                            <div data-oe-protected="false">
                                <p id="false">a[c1}{c1]</p>
                            </div>
                        </div>
                        <p>[c2}{c2]</p>
                    `));
                },
            });
        });
    });
    describe('data-oe-transient-content', () => {
        it('should send an empty transient-content element', async () => {
            await testMultiEditor({
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>[c1}{c1][c2}{c2]</p>',
                afterCreate: clientInfos => {
                    clientInfos.c1.editor.editable.prepend(...parseHTML(clientInfos.c1.editor.document, unformat(`
                        <div data-oe-transient-content="true">
                            <p>secret</p>
                        </div>
                    `)).children);
                    clientInfos.c1.editor.historyStep();
                    clientInfos.c2.editor.onExternalHistorySteps(
                        clientInfos.c1.editor._historySteps
                    );
                    testSameHistory(clientInfos);
                },
                afterCursorInserted:  clientInfos => {
                    chai.expect(clientInfos.c1.editable.innerHTML).to.equal(unformat(`
                        <div data-oe-transient-content="true">
                            <p>secret</p>
                        </div>
                        <p>[c1}{c1][c2}{c2]</p>
                    `));
                    chai.expect(clientInfos.c2.editable.innerHTML).to.equal(unformat(`
                        <div data-oe-transient-content="true"></div>
                        <p>[c1}{c1][c2}{c2]</p>
                    `));
                },
            });
        });
    });
    describe('post process external steps', () => {
        it('should properly await a processing promise before accepting new external steps.', async () => {
            const deferredPromise = new Deferred();
            const postProcessExternalSteps = (element) => {
                if (element.querySelector('.process')) {
                    setTimeout(() => {
                        deferredPromise.resolve();
                    });
                    return deferredPromise;
                }
                return null;
            };
            await testMultiEditor({
                options: {
                    postProcessExternalSteps: postProcessExternalSteps,
                },
                clientIds: ['c1', 'c2'],
                contentBefore: '<p>[c1}{c1][c2}{c2]</p>',
                afterCreate: async clientInfos => {
                    clientInfos.c1.editor.editable.append(...parseHTML(clientInfos.c1.editor.document, unformat(`
                        <div class="process">
                            <p>secret</p>
                        </div>
                    `)).children);
                    clientInfos.c1.editor.historyStep();
                    clientInfos.c1.editor.editable.append(...parseHTML(clientInfos.c1.editor.document, unformat(`
                        <p>post-process</p>
                    `)).children);
                    clientInfos.c1.editor.historyStep();
                    clientInfos.c2.editor.onExternalHistorySteps(
                        clientInfos.c1.editor._historySteps
                    );
                    chai.expect(clientInfos.c1.editable.innerHTML).to.equal(unformat(`
                        <p></p>
                        <div class="process">
                            <p>secret</p>
                        </div>
                        <p>post-process</p>
                    `));
                    chai.expect(clientInfos.c2.editable.innerHTML).to.equal(unformat(`
                        <p></p>
                        <div class="process">
                            <p>secret</p>
                        </div>
                    `));
                    await deferredPromise;
                    chai.expect(clientInfos.c2.editable.innerHTML).to.equal(unformat(`
                        <p></p>
                        <div class="process">
                            <p>secret</p>
                        </div>
                        <p>post-process</p>
                    `));
                    testSameHistory(clientInfos);
                },
            });
        });
    })
});
