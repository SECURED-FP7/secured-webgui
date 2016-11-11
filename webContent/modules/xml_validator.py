import logging

from lxml import etree


def validate(xmltext, schema):
    logger = logging.getLogger(__name__)
    
    # Encode XML to utf8
    xmltext = xmltext.encode('utf-8')
    
    # Get XML schema from file
    with open(schema, 'r') as f:
        schema_root = etree.XML(f.read())

    try:
        schema = etree.XMLSchema(schema_root)
        xmlparser = etree.XMLParser(schema=schema, ns_clean=True, encoding='utf-8')
        xml = etree.fromstring(xmltext, parser=xmlparser)
        logger.debug('MSPL ok')
        return True
    
    except:
        logger.exception('MSPL validation')
        raise
