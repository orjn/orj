# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import hashlib
from collections import OrderedDict
from werkzeug.urls import url_quote
from markupsafe import Markup

from orj import api, models, fields
from orj.tools import html_escape as escape


class Image(models.AbstractModel):
    """
    Widget options:

    ``class``
        set as attribute on the generated <img> tag
    """
    _name = 'ir.qweb.field.image'
    _description = 'Qweb Field Image'
    _inherit = 'ir.qweb.field.image'

    def _get_src_urls(self, record, field_name, options):
        """Considering the rendering options, returns the src and data-zoom-image urls.

        :return: src, src_zoom urls
        :rtype: tuple
        """
        max_size = None
        if options.get('resize'):
            max_size = options.get('resize')
        else:
            max_width, max_height = options.get('max_width', 0), options.get('max_height', 0)
            if max_width or max_height:
                max_size = '%sx%s' % (max_width, max_height)

        sha = hashlib.sha512(str(getattr(record, 'write_date', fields.Datetime.now())).encode('utf-8')).hexdigest()[:7]
        max_size = '' if max_size is None else '/%s' % max_size

        if options.get('filename-field') and options['filename-field'] in record and record[options['filename-field']]:
            filename = record[options['filename-field']]
        elif options.get('filename'):
            filename = options['filename']
        else:
            filename = record.display_name
        filename = (filename or 'name').replace('/', '-').replace('\\', '-').replace('..', '--')

        src = '/web/image/%s/%s/%s%s/%s?unique=%s' % (record._name, record.id, options.get('preview_image', field_name), max_size, url_quote(filename), sha)

        src_zoom = None
        if options.get('zoom') and getattr(record, options['zoom'], None):
            src_zoom = '/web/image/%s/%s/%s%s/%s?unique=%s' % (record._name, record.id, options['zoom'], max_size, url_quote(filename), sha)
        elif options.get('zoom'):
            src_zoom = options['zoom']

        return src, src_zoom

    @api.model
    def record_to_html(self, record, field_name, options):
        assert options['tagName'] != 'img',\
            "Oddly enough, the root tag of an image field can not be img. " \
            "That is because the image goes into the tag, or it gets the " \
            "hose again."

        src = src_zoom = None
        if options.get('qweb_img_raw_data', False):
            value = record[field_name]
            if value is False:
                return False
            src = self._get_src_data_b64(value, options)
        else:
            src, src_zoom = self._get_src_urls(record, field_name, options)

        aclasses = ['img', 'img-fluid'] if options.get('qweb_img_responsive', True) else ['img']
        aclasses += options.get('class', '').split()
        classes = ' '.join(map(escape, aclasses))

        if options.get('alt-field') and options['alt-field'] in record and record[options['alt-field']]:
            alt = escape(record[options['alt-field']])
        elif options.get('alt'):
            alt = options['alt']
        else:
            alt = escape(record.display_name)

        itemprop = None
        if options.get('itemprop'):
            itemprop = options['itemprop']

        atts = OrderedDict()
        atts["src"] = src
        atts["itemprop"] = itemprop
        atts["class"] = classes
        atts["style"] = options.get('style')
        atts["width"] = options.get('width')
        atts["height"] = options.get('height')
        atts["alt"] = alt
        atts["data-zoom"] = src_zoom and u'1' or None
        atts["data-zoom-image"] = src_zoom
        atts["data-no-post-process"] = options.get('data-no-post-process')

        atts = self.env['ir.qweb']._post_processing_att('img', atts)

        img = ['<img']
        for name, value in atts.items():
            if value:
                img.append(' ')
                img.append(escape(name))
                img.append('="')
                img.append(escape(value))
                img.append('"')
        img.append('/>')

        return Markup(''.join(img))

class ImageUrlConverter(models.AbstractModel):
    _description = 'Qweb Field Image'
    _inherit = 'ir.qweb.field.image_url'

    def _get_src_urls(self, record, field_name, options):
        image_url = record[options.get('preview_image', field_name)]
        return image_url, options.get("zoom", None)
