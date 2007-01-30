from gettext import gettext as _

class Reportable:
    """Base class for all the errors, warnings and suggestions."""
    text = "" 
    def __init__(self, extra = None):
        self.extra = extra
        self.context = ""
        if hasattr(self, 'pace'):
            self.extra = self.extra + ("\n   [Pace%s]" % self.pace)

    def tostring(self):
        return self.context + "\n" + self.text + "\n" + self.extra 

    def toshortstring(self):
        return self.context + " : " + self.text


# Every report should subclass one of these three classes, 
# which will make filtering of results easy.
class Error(Reportable): pass 
class Warning(Reportable): pass
class Suggestion(Reportable): pass


class ServerShouldHandleI18NContent(Suggestion):
    text = _('Server has discarded or been unable to handle i18n content.')

class ShouldSupportCacheValidators(Suggestion):
    text = _('GET should support the use of ETags and/or Last-Modifed cache validators.')

class ShouldSupportCompression(Suggestion):
    text = _('GET should support the use of compression to speed of transfers.')

class MustUseValidAtom(Error):
    text = _('Atom entries and feeds MUST be valid. [RFC 4287]')

class AtomShouldViolation(Warning):
    text = _('Violation of a SHOULD directive of [RFC 4287]')

class MustRejectNonWellFormedAtom(Warning):
    text = _('A server SHOULD reject non-wellformed content. [XML 1.0 Section 5.1 Validating and Non-Validating Processors]')

class InternalErrorEncountered(Error):
    text = _('Internal error encountered. This error can occur if the site returned non-welllformed XML.')

class EntryCreationMustReturn201(Warning):
    text = _('When an entry is successfully created the server SHOULD return an HTTP status code of 201. [RFC 2616 Section 9.5 POST]')

class EntryCreationMustReturnLocationHeader(Error):
    text = _('When an entry is successfully created the server MUST return a Location: HTTP header. [APP-08 Section 8.1 Creating Resource with POST]')

class EntryCreationMustBeReflectedInFeed(Error):
    text = _('When an entry is successfully created it must be added to the associated feed. [APP-08 Section 8.1 Creating Resources.]')

class EntryDeletionFailed(Error):
    text = _('The status returned does not reflect a successful deletion.')

class EntryUpdateFailed(Error):
    text = _('The status returned does not reflect a successful update.')

class EntryDeletionMustBeReflectedInFeed(Error):
    text = _('When an entry is successfully deleted, the Member URI MUST be removed from the collection. ')
    pace = 'PaperTrail'

class LocationHeaderMustMatchLinkRelEdit(Error):
    text = _('The link/@rel="edit" URI must match the URI returned via the Location: HTTP header during creation.') 
    pace = 'PaperTrail'

class GetFailedOnMemberResource(Error):
    text = _('Could not dereference the Member URI.')


