import re
import logging
from pymarc import Field
from pymarc import Record

class AlephSeqReader:

    def __init__(self, file_path):
        self.file = file_path
        self.current_line = self.file.readline().rstrip()
        self.fields = []
        self.field = None

    def __iter__(self):
        return self
    
    def close(self):
        self.file.close()

    def __next__(self):
        if self.current_line == '':
            raise StopIteration 
        current_id = self.current_line[0:9]
        self.record = Record()
        while True: 
            current_id = self.current_line[0:9]
            field = self.form_field(self.current_line)
            self.record.add_field(field)
            self.previous_line = self.current_line
            self.current_line = self.file.readline().rstrip()
            if self.current_line[0:9] != current_id:
                if self.record['DEL']:
                    return ""
                elif self.record['STA']:
                    for field in self.record.get_fields("STA"):
                        for sf in field.get_subfields('a'):
                            if sf == "DELETED":
                                return ""
                # add identifier for testing
                if not self.record['001']:
                    field = Field(tag='001', data=current_id)
                    self.record.add_ordered_field(field)
                return self.record
                    
    def form_field(self, line):
        fields = re.split('\$\$', line)
        tag = fields[0][10:13]
        indicators = [fields[0][13], fields[0][14]]
        if tag == "LDR":
            self.record.leader = fields[0][18:]
        field = Field(tag, indicators, [])
        if len(fields) > 1:
            for f in fields[1:]:
                try:
                    field.add_subfield(f[0], f[1:])
                except IndexError:
                    logging.error("indexError %s"%(line))    
        else:  
            try:
                field.data = fields[0][18:]    
            except IndexError:
                    logging.error("indexError %s"%(line))   
        return field  