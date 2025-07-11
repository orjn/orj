# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

MISC_HTML_SOURCE = u"""
<font size="2" style="color: rgb(31, 31, 31); font-family: monospace; font-variant: normal; line-height: normal; ">test1</font>
<div style="color: rgb(31, 31, 31); font-family: monospace; font-variant: normal; line-height: normal; font-size: 12px; font-style: normal; ">
<b>test2</b></div><div style="color: rgb(31, 31, 31); font-family: monospace; font-variant: normal; line-height: normal; font-size: 12px; ">
<i>test3</i></div><div style="color: rgb(31, 31, 31); font-family: monospace; font-variant: normal; line-height: normal; font-size: 12px; ">
<u>test4</u></div><div style="color: rgb(31, 31, 31); font-family: monospace; font-variant: normal; line-height: normal; font-size: 12px; ">
<strike>test5</strike></div><div style="color: rgb(31, 31, 31); font-family: monospace; font-variant: normal; line-height: normal; ">
<font size="5">test6</font></div><div><ul><li><font color="#1f1f1f" face="monospace" size="2">test7</font></li><li>
<font color="#1f1f1f" face="monospace" size="2">test8</font></li></ul><div><ol><li><font color="#1f1f1f" face="monospace" size="2">test9</font>
</li><li><font color="#1f1f1f" face="monospace" size="2">test10</font></li></ol></div></div>
<blockquote style="margin: 0 0 0 40px; border: none; padding: 0px;"><div><div><div><font color="#1f1f1f" face="monospace" size="2">
test11</font></div></div></div></blockquote><blockquote style="margin: 0 0 0 40px; border: none; padding: 0px;">
<blockquote style="margin: 0 0 0 40px; border: none; padding: 0px;"><div><font color="#1f1f1f" face="monospace" size="2">
test12</font></div><div><font color="#1f1f1f" face="monospace" size="2"><br></font></div></blockquote></blockquote>
<font color="#1f1f1f" face="monospace" size="2"><a href="http://google.com">google</a></font>
<a href="javascript:alert('malicious code')">test link</a>
"""

EDI_LIKE_HTML_SOURCE = u"""<div style="font-family: 'Lucida Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
    <p>Hello {{ object.partner_id.name }},</p>
    <p>A new invoice is available for you: </p>
    <p style="border-left: 1px solid #8e0000; margin-left: 30px;">
       &nbsp;&nbsp;<strong>REFERENCES</strong><br />
       &nbsp;&nbsp;Invoice number: <strong>{{ object.number }}</strong><br />
       &nbsp;&nbsp;Invoice total: <strong>{{ object.amount_total }} {{ object.currency_id.name }}</strong><br />
       &nbsp;&nbsp;Invoice date: {{ object.invoice_date }}<br />
       &nbsp;&nbsp;Order reference: {{ object.origin }}<br />
       &nbsp;&nbsp;Your contact: <a href="mailto:{{ object.user_id.email or '' }}?subject=Invoice%20{{ object.number }}">{{ object.user_id.name }}</a>
    </p>
    <br/>
    <p>It is also possible to directly pay with Paypal:</p>
    <a style="margin-left: 120px;" href="{{ object.paypal_url }}">
        <img class="oe_edi_paypal_button" src="https://www.paypal.com/en_US/i/btn/btn_paynowCC_LG.gif"/>
    </a>
    <br/>
    <p>If you have any question, do not hesitate to contact us.</p>
    <p>Thank you for choosing {{ object.company_id.name or 'us' }}!</p>
    <br/>
    <br/>
    <div style="width: 375px; margin: 0px; padding: 0px; background-color: #8E0000; border-top-left-radius: 5px 5px; border-top-right-radius: 5px 5px; background-repeat: repeat no-repeat;">
        <h3 style="margin: 0px; padding: 2px 14px; font-size: 12px; color: #DDD;">
            <strong style="text-transform:uppercase;">{{ object.company_id.name }}</strong></h3>
    </div>
    <div style="width: 347px; margin: 0px; padding: 5px 14px; line-height: 16px; background-color: #F2F2F2;">
        <span style="color: #222; margin-bottom: 5px; display: block; ">
        {{ object.company_id.street }}<br/>
        {{ object.company_id.street2 }}<br/>
        {{ object.company_id.zip }} {{ object.company_id.city }}<br/>
        {{ object.company_id.state_id and ('%s, ' % object.company_id.state_id.name) or '' }} {{ object.company_id.country_id.name or '' }}<br/>
        </span>
        <div style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; ">
            Phone:&nbsp; {{ object.company_id.phone }}
        </div>
        <div>
            Web :&nbsp;<a href="{{ object.company_id.website }}">{{ object.company_id.website }}</a>
        </div>
    </div>
</div></body></html>"""


# QUOTES

QUOTE_BLOCKQUOTE = u"""<html>
  <head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
  </head>
  <body text="#000000" bgcolor="#FFFFFF">
    <div class="moz-cite-prefix">On 05-01-16 05:52, Andreas Becker
      wrote:<br>
    </div>
    <blockquote
cite="mid:CAEJSRZvWvud8c6Qp=wfNG6O1+wK3i_jb33qVrF7XyrgPNjnyUA@mail.gmail.com"
      type="cite"><base href="https://www.orj.net">
      <div dir="ltr">Yep Dominique that is true, as Postgres was the
        base of all same as Orj and MySQL etc came much later.Â 
        <div><br>
        </div>
        <div>Unfortunately many customers who ask for and ERP are with
          hosters which still don't provide Postgres and MySQL is
          available everywhere. Additionally Postgres seems for many
          like a big black box while MySQL is very well documented and
          understandable and it has PHPmyAdmin which is far ahead of any
          tool managing postgres DBs.</div>
        <br>
      </div>
    </blockquote>
    <br>
    I don't care how much you are highlighting the advantages of Erpnext
    on this Orj mailinglist, but when you start implying that Postgres
    is not well documented it really hurts.<br>
    <br>
    <pre class="moz-signature" cols="72">-- 
Opener B.V. - Business solutions driven by open source collaboration

Stefan Rijnhart - Consultant/developer

mail: <a class="moz-txt-link-abbreviated" href="mailto:stefan@opener.am">stefan@opener.am</a>
tel: +31 (0) 20 3090 139
web: <a class="moz-txt-link-freetext" href="https://opener.am">https://opener.am</a></pre>
  </body>
</html>"""

QUOTE_BLOCKQUOTE_IN = [u"""<blockquote cite="mid:CAEJSRZvWvud8c6Qp=wfNG6O1+wK3i_jb33qVrF7XyrgPNjnyUA@mail.gmail.com" type="cite" data-o-mail-quote-node="1" data-o-mail-quote="1">"""]
QUOTE_BLOCKQUOTE_OUT = [u"""-- 
Opener B.V. - Business solutions driven by open source collaboration

Stefan Rijnhart - Consultant/developer"""]


QUOTE_THUNDERBIRD_HTML = u"""<html>
  <head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
  </head>
  <body text="#000000" bgcolor="#FFFFFF">
    <div class="moz-cite-prefix">On 01/05/2016 10:24 AM, Raoul
      Poilvache wrote:<br>
    </div>
    <blockquote
cite="mid:CAP76m_WWFH2KVrbjOxbaozvkmbzZYLWJnQ0n0sy9XpGaCWRf1g@mail.gmail.com"
      type="cite">
      <div dir="ltr"><b><i>Test reply. The suite.</i></b><br clear="all">
        <div><br>
        </div>
        -- <br>
        <div class="gmail_signature">Raoul Poilvache</div>
      </div>
    </blockquote>
    Top cool !!!<br>
    <br>
    <pre class="moz-signature" cols="72">-- 
Raoul Poilvache
</pre>
  </body>
</html>"""


QUOTE_THUNDERBIRD_HTML_IN = [u"""<blockquote cite="mid:CAP76m_WWFH2KVrbjOxbaozvkmbzZYLWJnQ0n0sy9XpGaCWRf1g@mail.gmail.com" type="cite" data-o-mail-quote-node="1" data-o-mail-quote="1">"""]
QUOTE_THUNDERBIRD_HTML_OUT = [u"""<pre class="moz-signature" cols="72"><span data-o-mail-quote="1">-- 
Raoul Poilvache
</span></pre>"""]


QUOTE_HOTMAIL_HTML = u"""
<html>
<head>
<style><!--
.hmmessage P
{
margin:0px=3B
padding:0px
}
body.hmmessage
{
font-size: 12pt=3B
font-family:Calibri
}
--></style></head>
<body class='hmmessage'>
<div dir='ltr'>I don't like that.<br><br>
<div><hr id="stopSpelling">
Date: Tue=2C 5 Jan 2016 10:24:48 +0100<br>
Subject: Test from gmail<br>
From: poilvache@example.com<br>
To: tartelette@example.com grosbedon@example.com<br><br>
<div dir="ltr"><b><i>Test reply. The suite.</i></b>
<br clear="all"><div><br>
</div>-- <br><div class="ecxgmail_signature">
Raoul Poilvache</div>
</div></div></div></body></html>"""
QUOTE_HOTMAIL_HTML_IN = [u"""I don't like that.<br><br>"""]
QUOTE_HOTMAIL_HTML_OUT = [
    u"""<hr id="stopSpelling" data-o-mail-quote="1">""",
    u"""<div dir="ltr" data-o-mail-quote="1"><b data-o-mail-quote="1"><i data-o-mail-quote="1">Test reply. The suite.</i></b>"""]


QUOTE_OUTLOOK_HTML = """
<html>
   <head>
      <meta http-equiv="Content-Type" content="text/html; charset=3Diso-8859-=
         1">
      <style type="text/css" style="display:none;"> P {margin-top:0;margin-bo=
         ttom:0;}
      </style>
   </head>
   <body dir="ltr">
      <div id="mail_body">
         Reply from outlook
      </div>
      <div style="font-family: Calibri, Helvetica, sans-serif; font-size: 12pt;=
         color: rgb(0, 0, 0);">
         <br>
      </div>
         <div class="elementToProof" id="Signature">John</div>
         <div id="appendonsend"></div>
         <div style="font-family:Calibri,Helvetica,sans-serif; font-size:12pt; col=
            or:rgb(0,0,0)">
            <br>
         </div>
         <hr tabindex="-1" style="display:inline-block; width:98%">
         <div id="divRplyFwdMsg" dir="ltr">
            <font face="Calibri, sans-serif" color="#000000" style="font-size:11pt"><b>De :</b> test@example.com<br>
            <b>=C0 :</b> test@example.com &lt;test@example.com&gt;<br>
            <b>Objet :</b> Parent message</font>
            <div>&nbsp;</div>
         </div>
         <div>
            <div dir="ltr">Parent email body</div>
         </div>
   </body>
</html>
"""

QUOTE_OUTLOOK_HTML_IN = [
    """Reply from outlook""",
    """<div id="mail_body">""",
]
QUOTE_OUTLOOK_HTML_OUT = [
    """<div class="elementToProof" id="Signature" data-o-mail-quote-container="1" data-o-mail-quote="1">John</div>""",
    """<div id="appendonsend" data-o-mail-quote-container="1" data-o-mail-quote="1"></div>""",  # quoted when empty in case there's a signature before
    """<hr tabindex="-1" style="display:inline-block; width:98%" data-o-mail-quote="1">""",
    """<div data-o-mail-quote-container="1" data-o-mail-quote="1">
            <div dir="ltr" data-o-mail-quote="1">Parent email body</div>
         </div>""",
    """<div id="divRplyFwdMsg" dir="ltr" data-o-mail-quote-container="1" data-o-mail-quote="1">""",
]


QUOTE_THUNDERBIRD_1 = u"""<div>On 11/08/2012 05:29 PM,
      <a href="mailto:dummy@example.com">dummy@example.com</a> wrote:<br></div>
    <blockquote>
      <div>I contact you about our meeting for tomorrow. Here is the
        schedule I propose:</div>
      <div>
        <ul><li>9 AM: brainstorming about our new amazing business
            app&lt;/span&gt;&lt;/li&gt;</li>
          <li>9.45 AM: summary</li>
          <li>10 AM: meeting with Fabien to present our app</li>
        </ul></div>
      <div>Is everything ok for you?</div>
      <div>
        <p>--<br>
          Administrator</p>
      </div>
      <div>
        <p>Log in our portal at:
<a href="http://localhost:8069#action=login&amp;db=mail_1&amp;token=rHdWcUART5PhEnJRaXjH">http://localhost:8069#action=login&amp;db=mail_1&amp;token=rHdWcUART5PhEnJRaXjH</a></p>
      </div>
    </blockquote>
    Ok for me. I am replying directly below your mail, using Thunderbird, with a signature.<br><br>
    Did you receive my email about my new laptop, by the way?<br><br>
    Raoul.<br><pre>-- 
Raoul Grosbedonn&#233;e
</pre>"""

QUOTE_THUNDERBIRD_1_IN = [
    u'<a href="mailto:dummy@example.com">dummy@example.com</a> ',
    u'<blockquote data-o-mail-quote-node="1" data-o-mail-quote="1">',
    u'Ok for me. I am replying directly below your mail, using Thunderbird, with a signature.']
QUOTE_THUNDERBIRD_1_OUT = [u"""-- 
Raoul Grosbedonnée
"""]

QUOTE_YAHOO_HTML = """
<html>
   <head></head>
   <body>
      <div class="ydpf6e951dcyahoo-style-wrap">
      <div></div>
      <div dir="ltr" data-setdir="false">Reply from Yahoo</div>
      </div>
      <div id="yahoo_quoted_8820595126" class="yahoo_quoted">
         <div style="font-family:'Helvetica Neue', Helvetica, Arial, sans-serif;font-size:13px;color:#26282a;">
            =20
            <div>
               Bob a dit:
            </div>
            <div><br></div>
            <div><br></div>
            <div>
               <div id="yiv3215395356">
                  <div dir="ltr">Parent email body</div>
               </div>
            </div>
         </div>
      </div>
   </body>
</html>
"""

QUOTE_YAHOO_HTML_IN = [
    """Reply from Yahoo""",
    """<div dir="ltr" data-setdir="false">""",
    """<div class="ydpf6e951dcyahoo-style-wrap">""",
]
QUOTE_YAHOO_HTML_OUT = [
    """<div id="yahoo_quoted_8820595126" class="yahoo_quoted" data-o-mail-quote="1">""",
]


TEXT_1 = u"""I contact you about our meeting tomorrow. Here is the schedule I propose:
9 AM: brainstorming about our new amazing business app
9.45 AM: summary
10 AM: meeting with Ignasse to present our app
Is everything ok for you?
--
MySignature"""

TEXT_1_IN = [u"""I contact you about our meeting tomorrow. Here is the schedule I propose:
9 AM: brainstorming about our new amazing business app
9.45 AM: summary
10 AM: meeting with Ignasse to present our app
Is everything ok for you?"""]
TEXT_1_OUT = [u"""
--
MySignature"""]

TEXT_2 = u"""Salut Raoul!
Le 28 oct. 2012 à 00:02, Raoul Grosbedon a écrit :

> I contact you about our meeting tomorrow. Here is the schedule I propose: (quote)

Of course. This seems viable.

> 2012/10/27 Bert Tartopoils :
>> blahblahblah (quote)?
>> 
>> blahblahblah (quote)
>> 
>> Bert TARTOPOILS
>> bert.tartopoils@miam.miam
>> 
> 
> 
> -- 
> RaoulSignature

--
Bert TARTOPOILS
bert.tartopoils@miam.miam
"""

TEXT_2_IN = [u"Salut Raoul!", "Of course. This seems viable."]
TEXT_2_OUT = [u"""
> I contact you about our meeting tomorrow. Here is the schedule I propose: (quote)""",
"""
> 2012/10/27 Bert Tartopoils :
>> blahblahblah (quote)?
>> 
>> blahblahblah (quote)
>> 
>> Bert TARTOPOILS
>> bert.tartopoils@miam.miam
>> 
> 
> 
> -- 
> RaoulSignature"""]

# MISC

GMAIL_1 = u"""Hello,<div><br></div><div>Ok for me. I am replying directly in gmail, with signature.</div><div><br></div><div>Kind regards,</div><div><br></div><div>Demo.<br><br>
<div class="gmail_quote">
<div dir="ltr" class="gmail_attr">On Thu, Nov 8, 2012 at 5:29 PM,  <span>&lt;<a href="mailto:dummy@example.com">dummy@example.com</a>&gt;</span> wrote:<br>
<blockquote class="gmail_quote"><div>I contact you about our meeting for tomorrow. Here is the schedule I propose:</div><div><ul><li>9 AM: brainstorming about our new amazing business app&lt;/span&gt;&lt;/li&gt;</li>
<li>9.45 AM: summary</li><li>10 AM: meeting with Fabien to present our app</li></ul></div><div>Is everything ok for you?</div>
<div><p>-- <br>Administrator</p></div>

<div><p>Log in our portal at: <a href="http://localhost:8069#action=login&amp;db=mail_1&amp;login=demo">http://localhost:8069#action=login&amp;db=mail_1&amp;login=demo</a></p></div>
</blockquote>
<div><br clear="all"></div>
<div><br></div>
<span class="gmail_signature_prefix">-- </span><br>
<div dir="ltr" class="gmail_signature">
    <div dir="ltr">
        This is a test signature
        <div><br></div>
        <div>123</div>
    </div>
</div>
</div><br></div>"""

GMAIL_1_IN = [
    u'Ok for me. I am replying directly in gmail, with signature.',
    '<div class="gmail_quote" data-o-mail-quote-container="1" data-o-mail-quote="1">',
    '<div dir="ltr" class="gmail_attr" data-o-mail-quote="1">On Thu, Nov 8, 2012 at 5:29 PM',
    '<blockquote class="gmail_quote" data-o-mail-quote-container="1" data-o-mail-quote="1" data-o-mail-quote-node="1">',
    # blank spaces between signature and reply quote should be quoted too
    '<div data-o-mail-quote="1"><br clear="all" data-o-mail-quote="1"></div>\n'
    '<div data-o-mail-quote="1"><br data-o-mail-quote="1"></div>',
]
GMAIL_1_OUT = []

HOTMAIL_1 = u"""<div>
    <div dir="ltr"><br>
        I have an amazing company, i'm learning Orj, it is a small company yet, but plannig to grow up quickly.
        <br><br>Kindest regards,<br>xxx<br>
        <div>
            <div id="SkyDrivePlaceholder">
            </div>
            <hr id="stopSpelling">
            Subject: Re: your Orj.net registration<br>From: xxx@xxx.xxx<br>To: xxx@xxx.xxx<br>Date: Wed, 27 Mar 2013 17:12:12 +0000
            <br><br>
            Hello xxx,
            <br>
            I noticed you recently created an Orj.net account to access Orj Apps.
            <br>
            You indicated that you wish to use Orj in your own company.
            We would like to know more about your your business needs and requirements, and see how
            we can help you. When would you be available to discuss your project?<br>
            Best regards,<br>
            <pre>
                <a href="http://orj.net" target="_blank">http://orj.net</a>
                Belgium: +32.81.81.37.00
                U.S.: +1 (650) 307-6736
                India: +91 (79) 40 500 100
            </pre>
        </div>
    </div>
</div>"""
HOTMAIL_1_IN = [u"""<div dir="ltr"><br>
        I have an amazing company, i'm learning Orj, it is a small company yet, but plannig to grow up quickly.
        <br><br>Kindest regards,<br>xxx<br>"""]
HOTMAIL_1_OUT = [
    u"""<hr id="stopSpelling" data-o-mail-quote="1">""",
    u"""<pre data-o-mail-quote="1">
                <a href="http://orj.net" target="_blank" data-o-mail-quote="1">http://orj.net</a>
                Belgium: +32.81.81.37.00
                U.S.: +1 (650) 307-6736
                India: +91 (79) 40 500 100
            </pre>"""]

MSOFFICE_1 = u"""
<div>
<div class="WordSection1">
        <p class="MsoNormal">
            <span style="font-size:11.0pt;font-family:&quot;Calibri&quot;,&quot;sans-serif&quot;;color:#1F497D">
                Our requirements are simple. Just looking to replace some spreadsheets for tracking quotes and possibly using the timecard module.
                We are a company of 25 engineers providing product design services to clients.
            </span>
        </p>
        <p></p>
        <p></p>
        <p class="MsoNormal">
            <span style="font-size:11.0pt;font-family:&quot;Calibri&quot;,&quot;sans-serif&quot;;color:#1F497D">
                I’ll install on a windows server and run a very limited trial to see how it works.
                If we adopt Orj we will probably move to Linux or look for a hosted SaaS option.
            </span>
        </p>
        <p></p>
        <p></p>
        <p class="MsoNormal">
            <span style="font-size:11.0pt;font-family:&quot;Calibri&quot;,&quot;sans-serif&quot;;color:#1F497D">
                <br>
                I am also evaluating Adempiere and maybe others.
            </span>
        </p>
        <p></p>
        <p></p>
        <p class="MsoNormal">
            <span style="font-size:11.0pt;font-family:&quot;Calibri&quot;,&quot;sans-serif&quot;;color:#1F497D">
            </span>
        </p>
        <p>&nbsp;</p>
        <p></p>
        <p class="MsoNormal">
            <span style="font-size:11.0pt;font-family:&quot;Calibri&quot;,&quot;sans-serif&quot;;color:#1F497D">
                I expect the trial will take 2-3 months as this is not a high priority for us.
            </span>
        </p>
        <p></p>
        <p></p>
        <p class="MsoNormal">
            <span style="font-size:11.0pt;font-family:&quot;Calibri&quot;,&quot;sans-serif&quot;;color:#1F497D">
            </span>
        </p>
        <p>&nbsp;</p>
        <p></p>
        <p class="MsoNormal">
            <span style="font-size:11.0pt;font-family:&quot;Calibri&quot;,&quot;sans-serif&quot;;color:#1F497D">
                Alan
            </span>
        </p>
        <p></p>
        <p></p>
        <p class="MsoNormal">
            <span style="font-size:11.0pt;font-family:&quot;Calibri&quot;,&quot;sans-serif&quot;;color:#1F497D">
            </span>
        </p>
        <p>&nbsp;</p>
        <p></p>
        <div>
            <div style="border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in">
                <p class="MsoNormal">
                    <b><span style="font-size:10.0pt;font-family:&quot;Tahoma&quot;,&quot;sans-serif&quot;">
                        From:
                    </span></b>
                    <span style="font-size:10.0pt;font-family:&quot;Tahoma&quot;,&quot;sans-serif&quot;">
                        Orj Ore [mailto:sales@orj.net]
                        <br><b>Sent:</b> Monday, 11 March, 2013 14:47<br><b>To:</b> Alan Widmer<br><b>Subject:</b> Re: your Orj.net registration
                    </span>
                </p>
                <p></p>
                <p></p>
            </div>
        </div>
        <p class="MsoNormal"></p>
        <p>&nbsp;</p>
        <p>Hello Alan Widmer, </p>
        <p></p>
        <p>I noticed you recently downloaded Orj. </p>
        <p></p>
        <p>
            Uou mentioned you wish to use Orj in your own company. Please let me more about your
            business needs and requirements? When will you be available to discuss about your project?
        </p>
        <p></p>
        <p>Thanks for your interest in Orj, </p>
        <p></p>
        <p>Feel free to contact me if you have any questions, </p>
        <p></p>
        <p>Looking forward to hear from you soon. </p>
        <p></p>
        <pre><p>&nbsp;</p></pre>
        <pre>--<p></p></pre>
        <pre>Nicolas<p></p></pre>
        <pre><a href="http://orj.net">http://orj.net</a><p></p></pre>
        <pre>Belgium: +32.81.81.37.00<p></p></pre>
        <pre>U.S.: +1 (650) 307-6736<p></p></pre>
        <pre>India: +91 (79) 40 500 100<p></p></pre>
        <pre>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<p></p></pre>
    </div>
</div>"""

MSOFFICE_1_IN = [u'Our requirements are simple. Just looking to replace some spreadsheets for tracking quotes and possibly using the timecard module.']
MSOFFICE_1_OUT = [u'I noticed you recently downloaded Orj.', 'Uou mentioned you wish to use Orj in your own company.', 'Belgium: +32.81.81.37.00']


# ------------------------------------------------------------
# Test cases coming from bugs
# ------------------------------------------------------------

# bug: read more not apparent, strange message in read more span
BUG1 = u"""<pre>Hi Migration Team,

Paragraph 1, blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah.

Paragraph 2, blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah.

Paragraph 3, blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah blah blah blah blah blah blah 
blah blah blah blah blah blah blah blah.

Thanks.

Regards,

-- 
Olivier Laurent
Migration Manager
Orj SA
Chaussée de Namur, 40
B-1367 Gérompont
Tel: +32.81.81.37.00
Web: http://www.orj.net</pre>"""

BUG_1_IN = [
    u'Hi Migration Team',
    u'Paragraph 1'
]
BUG_1_OUT = [u"""
-- 
Olivier Laurent
Migration Manager
Orj SA
Chaussée de Namur, 40
B-1367 Gérompont
Tel: +32.81.81.37.00
Web: http://www.orj.net"""]


REMOVE_CLASS = u"""
<div style="FONT-SIZE: 12pt; FONT-FAMILY: 'Times New Roman'; COLOR: #000000">
    <div>Hello</div>
    <div>I have just installed Orj 9 and I've got the following error:</div>
    <div>&nbsp;</div>
    <div class="orj orj_webclient_container oe_webclient">
        <div class="oe_loading" style="DISPLAY: none">&nbsp;</div>
    </div>
    <div class="modal-backdrop in"></div>
    <div role="dialog" tabindex="-1" aria-hidden="false" class="modal in" style="DISPLAY: block" data-backdrop="static">
        <div class="modal-dialog modal-lg">
            <div class="modal-content orj">
                <div class="modal-header"> 
                    <h4 class="modal-title">Orj Error<span class="o_subtitle text-muted"></span></h4>
                </div>
                <div class="o_error_detail modal-body">
                    <pre>An error occurred in a modal and I will send you back the html to try opening one on your end</pre>
                </div>
            </div>
        </div>
    </div>
</div>
"""
REMOVE_CLASS_IN = [
    u'<div style="font-size:12pt; font-family:\'Times New Roman\'; color:#000000">',
    u'An error occurred in a modal and I will send you back the html to try opening one on your end']
REMOVE_CLASS_OUT = [
    u'<div class="modal-backdrop in">',
    u'<div class="modal-content orj">',
    u'<div class="modal-header">']
