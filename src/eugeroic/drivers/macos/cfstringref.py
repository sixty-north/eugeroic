import objc
from CoreFoundation import CFStringCreateWithCString, kCFStringEncodingUTF8


# noinspection PyUnresolvedReferences
def cfstringref(string: str):
    return objc.pyobjc_id(
        CFStringCreateWithCString(
            None,
            string.encode("utf-8"),
            kCFStringEncodingUTF8,
        ).nsstring()
    )



if __name__ == "__main__":
    # Test the function
    python_string = "Hello, CFStringRef!"
    cf_string_ref = cfstringref(python_string)
    print(cf_string_ref)