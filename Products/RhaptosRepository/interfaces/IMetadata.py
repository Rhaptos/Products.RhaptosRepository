from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class IMetadata(Interface):
    """
    Interface for the metadata supported by content objects in a repository
    """

    title = Attribute('title', 'The title of the object')

    abstract = Attribute('abstract', "A brief description or summary of the content")

    license = Attribute('license', "The content's license URL")
    
    created = Attribute('created', "A DateTime repsentation of when the first version of this content was created")

    revised = Attribute('revised', "A DateTime repsentation of when the this version was revised")

    keywords = Attribute('keywords', "A list of keywords or phrases")

    authors = Attribute('authors', "The usernames of this object's authors")

    parentAuthors = Attribute('parentAuthors', "The usernames of the authors of any parent works")

    maintainers = Attribute('maintainers', "The usernames of this object's maintainers")

    licensors = Attribute('licensors', "The usernames of this object's licensors (aka copyright holders)")

