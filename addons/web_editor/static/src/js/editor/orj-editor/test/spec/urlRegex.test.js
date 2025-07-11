/** @orj-module */

import { URL_REGEX } from '../../src/OrjEditor.js';

describe('urlRegex', () => {
    it('should match foo.com', () => {
        const url = 'foo.com';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match[0]).to.be.equal(url);
    });
    it('should not match foo.else', () => {
        const url = 'foo.else';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match).to.be.equal(null);
    });
    it('should match www.abc.abc', () => {
        const url = 'www.abc.abc';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match[0]).to.be.equal(url);
    });
    it('should match abc.abc.com', () => {
        const url = 'abc.abc.com';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match[0]).to.be.equal(url);
    });
    it('should not match abc.abc.abc', () => {
        const url = 'abc.abc.abc';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match).to.be.equal(null);
    });
    it('should match http://abc.abc.abc', () => {
        const url = 'http://abc.abc.abc';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match[0]).to.be.equal(url);
    });
    it('should match https://abc.abc.abc', () => {
        const url = 'https://abc.abc.abc';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match[0]).to.be.equal(url);
    });
    it('should match 1234-abc.runbot007.orj.net/web#id=3&menu_id=221', () => {
        const url = '1234-abc.runbot007.orj.net/web#id=3&menu_id=221';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match[0]).to.be.equal(url);
    });
    it('should match https://1234-abc.runbot007.orj.net/web#id=3&menu_id=221', () => {
        const url = 'https://1234-abc.runbot007.orj.net/web#id=3&menu_id=221';
        const text = `abc ${url} abc`;
        const match = text.match(URL_REGEX);
        chai.expect(match[0]).to.be.equal(url);
    });
});
