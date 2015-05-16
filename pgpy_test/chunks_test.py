
        ln = 224+13 #8192
        idx = 0
        sz = 8192
        lbyte = self.header.int_to_bytes(ln)

        chunk = self.ct[idx : idx+sz]
        print len(chunk)

        while len(chunk) > 8192:
            if idx > 0:
                _bytes += lbyte
            _bytes += chunk
            return bytes(_bytes)

            idx += sz
            chunk = self.ct[idx : idx+sz]


        return bytes(_bytes)

