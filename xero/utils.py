import re
import datetime


DATE = re.compile(
    r'^(\/Date\((?P<timestamp>-?\d+)((?P<offset_h>[-+]\d\d)(?P<offset_m>\d\d))?\)\/)'
    r'|'
    r'((?P<year>\d{4})-(?P<month>[0-2]\d)-0?(?P<day>[0-3]\d)'
    r'T'
    r'(?P<hour>[0-5]\d):(?P<minute>[0-5]\d):(?P<second>[0-6]\d))$'
)

OBJECT_NAMES = {
    "Attachments": "Attachment",
    "Accounts": "Account",
    "Allocations": "Allocation",
    "BankTransactions": "BankTransaction",
    "BankTransfers": "BankTransfer",
    "BrandingThemes": "BrandingTheme",
    "Contacts": "Contact",
    "CreditNotes": "CreditNote",
    "Currencies": "Currency",
    "Employees": "Employee",
    "ExpenseClaims": "ExpenseClaim",
    "Invoices": "Invoice",
    "Items": "Item",
    "Journals": "Journal",
    "ManualJournals": "ManualJournal",
    "Organisation": "Organisation",
    "Overpayments": "Overpayment",
    "Payments": "Payment",
    "Prepayments": "Prepayment",
    "Receipts": "Receipt",
    "RepeatingInvoices": "RepeatingInvoice",
    "Reports": "Report",
    "TaxRates": "TaxRate",
    "TrackingCategories": "TrackingCategory",
    "Users": "User",
    "Associations": "Association",
    "Files": "File",
    "Folders": "Folder",
    "Inbox": "Inbox",
    "LineItems": "LineItem",
}

def isplural(word):
    return word in OBJECT_NAMES.keys()

def singular(word):
    return OBJECT_NAMES.get(word)

def parse_date(string, force_datetime=False):
    """ Takes a Xero formatted date, e.g. /Date(1426849200000+1300)/"""
    matches = DATE.match(string)
    if not matches:
        return None

    values = dict([
        (
            k,
            v if v[0] in '+-' else int(v)
        ) for k,v in matches.groupdict().items() if v and int(v)
    ])

    if 'timestamp' in values:
        value = datetime.datetime.utcfromtimestamp(0) + datetime.timedelta(
            hours=int(values.get('offset_h', 0)),
            minutes=int(values.get('offset_m', 0)),
            seconds=int(values['timestamp']) / 1000.0
        )
        return value
        # Hmm not sure about this either: it returns a Date object
        # if the time is 00:00. See the note below. For now, we'll just
        # return the datetime, and allow end-user to handle it.
        if not value.time():
            return value.date()
        return value

    # I've made an assumption here, that a DateTime value will not
    # ever be YYYY-MM-DDT00:00:00, which is probably bad. I'm not
    # really sure how to handle this, other than to hard-code the
    # names of the field that are actually Date rather than DateTime.
    if len(values) > 3 or force_datetime:
        return datetime.datetime(**values)

    return date(**values)


def json_load_object_hook(dct):
    for key,value in dct.items():
        if isinstance(value, str) and value.startswith('/') and value.endswith('/'):
            value = parse_date(value)
            if value:
                dct[key] = value

    return dct
