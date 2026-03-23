import ssl
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend

class UnsafeEmailBackend(DjangoEmailBackend):
    """
    SMTP email backend that ignores SSL certificate verification.
    Use ONLY for debugging or when CA certificates are broken locally.
    """
    def open(self):
        if self.connection:
            return False
            
        try:
            # Create an unverified SSL context
            ssl_context = ssl._create_unverified_context()
            
            # Note: For port 465 (SSL), we pass the context to the class.
            # For port 587 (TLS), we use starttls later.
            
            self.connection = self.connection_class(
                self.host, self.port, timeout=self.timeout
            )
            
            if self.use_tls:
                self.connection.starttls(context=ssl_context)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False
