from django.views.i18n import render_javascript_catalog
import pdb
from django.conf import settings
import gettext as gettext_module
from django.utils import six
from django.utils.translation import check_for_language, to_locale, get_language

def get_javascript_catalog(locale, domain, packages):
    default_locale = to_locale(settings.LANGUAGE_CODE)
    packages = [p for p in packages if p == 'django.conf' or p in settings.INSTALLED_APPS]
    t = {}
    paths = []
    en_selected = locale.startswith('en')
    en_catalog_missing = True
    # paths of requested packages
    for package in packages:
        p = importlib.import_module(package)
        path = os.path.join(os.path.dirname(upath(p.__file__)), 'locale')
        paths.append(path)
    # add the filesystem paths listed in the LOCALE_PATHS setting
    paths.extend(list(reversed(settings.LOCALE_PATHS)))

    #we should selected the local first
    loaded=False
    for path in paths:
        try:
            catalog = gettext_module.translation(domain, path, [locale])
            t.update(catalog._catalog)
            loaded=True
        except IOError:
            pass

    #out the default
    if not loaded and locale != default_locale:
        # If the currently selected language is English but it doesn't have a
        # translation catalog (presumably due to being the language translated
        # from) then a wrong language catalog might have been loaded in the
        # previous step. It needs to be discarded.

        for path in paths:
            try:
                catalog = gettext_module.translation(domain, path, [default_locale])
                t.update(catalog._catalog)
            except IOError:
                pass

    plural = None
    if '' in t:
        for l in t[''].split('\n'):
            if l.startswith('Plural-Forms:'):
                plural = l.split(':', 1)[1].strip()
    if plural is not None:
        # this should actually be a compiled function of a typical plural-form:
        # Plural-Forms: nplurals=3; plural=n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;
        plural = [el.strip() for el in plural.split(';') if el.strip().startswith('plural=')][0].split('=', 1)[1]

    pdict = {}
    maxcnts = {}
    catalog = {}
    for k, v in t.items():
        if k == '':
            continue
        if isinstance(k, six.string_types):
            catalog[k] = v
        elif isinstance(k, tuple):
            msgid = k[0]
            cnt = k[1]
            maxcnts[msgid] = max(cnt, maxcnts.get(msgid, 0))
            pdict.setdefault(msgid, {})[cnt] = v
        else:
            raise TypeError(k)
    for k, v in pdict.items():
        catalog[k] = [v.get(i, '') for i in range(maxcnts[msgid] + 1)]

    #print '\nread file for djangojs\n'
    return catalog, plural


from django.views.decorators.cache import cache_page
from django.views.decorators.http import condition
import datetime
import hashlib

def get_version():
    # Write your own! That depends on your deployment strategy.
    # This example won't work if you release more than once a day.
    return datetime.date.today().isoformat()

# The javascript_catalog view may be cached server-side without limits,
# provided the cache is flushed when autoslave is upgraded and restarted.
key_prefix = 'js18n-%s' % get_version()
last_modified = datetime.datetime.now()
etag = hashlib.md5(key_prefix).hexdigest()

# @condition(etag_func=lambda req, **kw: etag,
#            last_modified_func=lambda req, **kw: last_modified)
# @cache_page(86400, key_prefix=key_prefix)
def javascript_catalog(request, domain='djangojs', packages=None):
    """
    Returns the selected language catalog as a javascript library.

    Receives the list of packages to check for translations in the
    packages parameter either from an infodict or as a +-delimited
    string from the request. Default is 'django.conf'.

    Additionally you can override the gettext domain for this view,
    but usually you don't want to do that, as JavaScript messages
    go to the djangojs domain. But this might be needed if you
    deliver your JavaScript source from Django templates.
    """
    locale = to_locale(get_language())

    if request.session and 'django_language' in request.session:
        if check_for_language(request.session['django_language']):
            locale = to_locale(request.session['django_language'])

    if request.GET and 'language' in request.GET:
        if check_for_language(request.GET['language']):
            locale = to_locale(request.GET['language'])

    if packages is None:
        packages = ['django.conf']
    if isinstance(packages, six.string_types):
        packages = packages.split('+')

    catalog, plural = get_javascript_catalog(locale, domain, packages)
    return render_javascript_catalog(catalog, plural)
