from django.core.management.base import BaseCommand, CommandError
from gavaconnect import api

class Command(BaseCommand):
    help = "Smoke-tests gavaconnect configuration by calling harmless endpoints with dummy values."

    def add_arguments(self, parser):
    parser.add_argument("--pin", help="KRA PIN to test PIN-by-PIN endpoint")
    parser.add_argument("--id", dest="idno", help="National ID to test PIN-by-ID")
    parser.add_argument("--type", dest="taxpayer_type", default="INDIVIDUAL")
    parser.add_argument("--prn", help="PRN to search")
    parser.add_argument("--vat", help="KRA PIN to test VAT exemption")  # Added

    def handle(self, *args, **opts):
        try:
            if opts.get("pin"):
                self.stdout.write(self.style.NOTICE("Testing PIN by PIN..."))
                self.stdout.write(str(api.pin_by_pin(opts["pin"])))
            if opts.get("idno"):
                self.stdout.write(self.style.NOTICE("Testing PIN by ID..."))
                self.stdout.write(str(api.pin_by_id(opts["idno"], opts["taxpayer_type"])))
            if opts.get("prn"):
                self.stdout.write(self.style.NOTICE("Testing PRN search..."))
                self.stdout.write(str(api.prn_search(opts["prn"])))
            if opts.get("vat"):  # Added
                self.stdout.write(self.style.NOTICE("Testing VAT exemption..."))
                self.stdout.write(str(api.vat_exemption(pin=opts["vat"])))
            self.stdout.write(self.style.SUCCESS("Self-test completed."))
        except Exception as ex:
            raise CommandError(str(ex))

