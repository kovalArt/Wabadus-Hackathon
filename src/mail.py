import dns.resolver


class MailServer:
    def __init__(self, domain):
        self.domain = domain 

    def dmarc_ckeck(self):
        try:
            response = dns.resolver.query('_dmarc.' + self.domain, 'TXT')
            dmarc_records = [record.to_text() for record in response if 'dmarc' in record.to_text().lower()]
            if len(dmarc_records) == 0:
                return {'values': 'failure'}
            return {'response': 'success', 'values': dmarc_records}
        except Exception as e:
            return {'response': 'error', 'values': str(e)}            

    def spf_check(self):
        try: 
            response = dns.resolver.query(self.domain, 'TXT')
            spf_records = [record.to_text() for record in response if 'v=spf1' in record.to_text().lower()]
            if len(spf_records) == 0:
                return {'response': 'failure'}
            return {'response': 'success', 'values': spf_records}
        except Exception as e:
            return {'response': 'error', 'values': str(e)}

    # TODO: Write dkim check function  
        

      