from io import BytesIO
import zipfile

from certx.common.model.models import CertificateContent


def compress_cert(cert_content: CertificateContent) -> bytes:
    if not cert_content:
        raise ValueError('cert_content is null')

    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        if cert_content.certificate:
            zf.writestr('cert.pem', cert_content.certificate)

        if cert_content.private_key:
            zf.writestr('key.pem', cert_content.private_key)

        if cert_content.certificate_chain:
            zf.writestr('chain.pem', b''.join(cert_content.certificate_chain))

    return zip_buf.getvalue()
