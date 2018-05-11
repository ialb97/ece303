




def fletcher_chksum(data):
        sum1 = 0
        sum2 = 0
        i = 0
        while i < len(data):
            sum1 = (sum1 + ord(data[i]))%65535
            sum2 = (sum2 + sum1)%65535
            i+=1
        x = sum1*65536 + sum2
        checksum = bytearray.fromhex('{:08x}'.format(x))
        pad = bytearray(32-len(checksum))
        return pad + checksum


fletcher_chksum('13PerthnWF3cRnAEjeY5S0OO58zhWQAB2FI17/9/kEIryqci74S2F0gvrF8jqfMopDI/h09BNT6fp3NPHf9kMGam6S7Yz/WXAcfqJqxb/bI0+dTt/W1g2dzPyIgK5JXYDRL9OwsJcviOJHFBrKBnvUdzJjBVNJhmmWh/2YoKO+HLEmUt146MjxGS5PodJVOPkTAvmOd6GAwc8v1qYa1HSGiFBRMandalyyvdN+EW53iYuPA39UnVfmMY9auCXbAYjQgM9P0chZH750vi/0wjU4m0OpFHsfvi5DWdLbCoVAb74hU7P+Ztm8u40Rn/l+lqzUP8nrDTGKwCjqtoNTKB51w21l1JKG7MM/WXsv+oRTEMS+I0sc+Dji2JnaYwupj5gcOCi/XCKCq2bqYa3kP/sxvcM2T+0D5OUUy++riohwYadHCYWNyUJmPYRZBCEfTQ7pRMro6HXF9/MDWJkKIu7sGgyJ7i/HWLRwWyISBMMgc4+gBeJOYAQFF1hkQAlLhKLN1NJi2+IKjmHcIhpTFPWwBIjYstEo0QG2NI3rdxTD8sTSZz3fyAkKfvZaEXDUIwzQQgJj61PsSEDO4kLnT+FDt5Mks93nGzOJpjS3odlEI7VCWOhQawKdiybzYyZBvt8yXGtXZ0O1rkyqCEn8leN/NLmqgdPFhoJOIzxdG9hYKL36eqtxaJEIGd+s7AiLTNCXFBb9XUmJ9f/ktgX/RRh188imoug+MEwnxCqCyxyvqDKCilIFryzAGisTlJtDNUhlwf3/1PnBdAWw5+FEHrEpLt+Ma0Tfis/9b0pEvLvIYenXwXr0C+qHkioTiq1o1YkVvYAA5m6JC4Htlwh2ZqoxqSiUxBUVtejxPwJ12jfqljVD2ZpVwoZ/f4MIQ6T1PckhWpjGbWIByB3MNAmXIm0R6lm18lUb3m4rQ6sLGtee/MBJFuF6y5QezMKFeUVE7ue2Z+MqqRQVg/EII2EUSeq9mc133I4m+Z1QucVnUNDn6B3huPQOz+V1vnyXdygjTMqZGDmfDCD+WayYnaHRq1+GFvVwDCNBsHdv6pHni3jXyu75mYMZ9W5ZH8Ga+ULkT9GrW2fXL14uPMe3ITVoOmYsZSeq4448+CYWptLvMgHL61IASh2pxjU/p')

