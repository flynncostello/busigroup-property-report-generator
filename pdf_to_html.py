from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO

output = StringIO()
with open('/Users/flynncostello/Library/CloudStorage/OneDrive-Personal/Work/BusiHealth & BusiVet/Site Report Automator/pdf_report_generator/output/Report.pdf', 'rb') as fin:
    extract_text_to_fp(fin, output, laparams=LAParams(), 
                      output_type='html', codec=None)

with open('output.html', 'w') as fout:
    fout.write(output.getvalue())