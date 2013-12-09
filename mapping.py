from openmetadata import process, constant


channel_to_file =   {
                        '.kvs': '.json',
                        '.txt': '.txt',
                        '.mdw': '.txt',
                    }


file_to_channel = dict([(v, k) for (k, v) in channel_to_file.items()])


datatype_to_key = {
                    dict:           '.json',
                    int:            '.json',
                    basestring:     '.txt',
                 }


key_to_channel = {
                    dict:   '.kvs',
                    int:    '.kvs',
                    str:    '.txt',
                 }


mapping =   {
                '.txt': process.DotTxt,
                '.mdw': process.DotMdw,
                '.json': process.DotJson
            }


# def convert(obj, upstream=False):
#     """Convert `obj` to its equivalent downstream value"""
#     return file_to_channel.get(obj) or channel_to_file.get(obj) or key_to_channel.get(obj)


def channelextension_from_keydatatype(datatype):
    if datatype in (dict, int, float, bool):
        return constant.Kvs
    if datatype in (basestring, unicode, str):
        # Todo: Determine if its Markdown first
        pass

    return constant.Txt

if __name__ == '__main__':
    pass
    # print convert('.kvs')
