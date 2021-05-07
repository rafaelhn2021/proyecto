import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import re
from datetime import datetime, date 


class mail_conf():
  
    def mail_to(self,mailto, usuario, entidad, mailaddress, mailpassword, nombre_smtp, puerto):
        message = MIMEMultipart("alternative")
        message["Subject"] = "Bienvenida SiDeclara"
        message["From"] = mailaddress
        message["To"] = mailto
        text = """\ """
        html = """\
		    <html lang="es">
		      <body>
		        <p>
                    Bienvenido(a) USUARIO
                    <br>
		            <br>
		            ENTIDAD te felicita de haberte registrado al sistema SiDeclara que se pone a tu disposición para cumplir con tus obligaciones como servidor público. 
                </p>
                <p>
		            ENTIDAD está segura de que este sistema te será de gran utilidad para ayudarnos a mantener la transparencia en nuestra imagen. 

		        </p>
		        <p>
		          <strong>ENTIDAD</strong><br>
		      
		        </p>
		      </body>
		    </html>
		"""
        soup=BeautifulSoup( html, features="html.parser")
        target= soup.find_all(text=re.compile(r'USUARIO'))
        for v in target:
    	    v.replace_with(v.replace('USUARIO', usuario))
        html=soup


        target= soup.find_all(text=re.compile(r'ENTIDAD'))
        for v in target:
    	    v.replace_with(v.replace('ENTIDAD', entidad))
    
        html=soup

        part1 = MIMEText(text, "plain")
        part2=MIMEText(html.encode('utf-8'), 'html','utf-8')
	
        message['Content-Type'] = "text/html; charset=utf-8"
        message.attach(part1)
        message.attach(part2)
        mailServer = smtplib.SMTP(nombre_smtp , puerto)
        mailServer.starttls()
        mailServer.login(mailaddress , mailpassword)
        try:
            mailServer.sendmail(mailaddress, mailto , message.as_string())
            print("\n Enviada la constancia!!!")
            mailServer.quit()
        finally:
            mailServer.close()

    
    def mail_to_iniciar(self,mailto, usuario, entidad, mailaddress, mailpassword, nombre_smtp, puerto):

        message = MIMEMultipart("alternative")
        message["Subject"] = "Inicio declaración"
        message["From"] = mailaddress
        message["To"] = mailto
        text = """\ """
        html = """\
            <html lang="es">
              <body>
               <p>Estimado USUARIO<br>
              <br>
                <p>
                 ENTIDAD gracias por iniciar tu declaración patrimonial, de intereses y fiscal.
                Esperamos que el cumplimiento de esta obligación se haga de manera sencilla para ti y dentro de los plazos establecidos.
                 Para cualquier problema no dudes en recurrir al OIC o al personal de apoyo técnico.

                </p>
                 <p>
                 Gracias <br> 
                 <strong>ENTIDAD</strong>
                </p>


          </body>
        </html>
        """
        soup=BeautifulSoup( html, features="html.parser")
        target= soup.find_all(text=re.compile(r'USUARIO'))
        for v in target:
            v.replace_with(v.replace('USUARIO', usuario))
        html=soup

        target= soup.find_all(text=re.compile(r'ENTIDAD'))
        for v in target:
            v.replace_with(v.replace('ENTIDAD', entidad))
    
        html=soup

        part1 = MIMEText(text, "plain")
        part2=MIMEText(html.encode('utf-8'), 'html','utf-8')
    
        message['Content-Type'] = "text/html; charset=utf-8"
        message.attach(part1)
        message.attach(part2)
        mailServer = smtplib.SMTP(nombre_smtp , puerto)
        mailServer.starttls()
        mailServer.login(mailaddress , mailpassword)
        try:
            mailServer.sendmail(mailaddress, mailto , message.as_string())
            print("\n Enviado!!!")
            mailServer.quit()
        finally:
            mailServer.close()
        

    def mail_to_final(self,mailto, usuario, apellido1, apellido2, entidad, folio, tipo, mailaddress, mailpassword, nombre_smtp, puerto):


        message = MIMEMultipart("alternative")
        message["Subject"] = "Término declaración"
        message["From"] = mailaddress
        message["To"] = mailto
        text = """\ """
        html = """\
            <html lang="es">
              <body>
                <p>Estimado(a) USUARIO APELLIDOS
                <p style="text-align:justify;">
                    Hemos recibido tu declaración terminada exitosamente y esta ha sido registrada en el sistema con el folio <strong>FOLIO</strong> el día <strong>FECHA</strong>.
                <br>
                <br>
                Esta <strong>Declaración de Situación Patrimonial</strong> y de Intereses es testimonio de haber cumplido en tiempo con su obligación. 
                <br>Su contenido puede estar sujeto a revisión y verificación por parte del Órgano Interno de Control.
                <br>
                <br>
                    Por favor, imprima este correo y presentelo al OIC de su ente público.
                </p>
                <br><br>
                <br><br>
                <p style="text-align:center;">
                __________________________________<br>
                    Sello y firma del OIC
                </p>
                <p>Fecha de recepción: _____________</p>
          </body>
        </html>
        """
        soup=BeautifulSoup( html, features="html.parser")
        target= soup.find_all(text=re.compile(r'USUARIO'))
        for v in target:
            v.replace_with(v.replace('USUARIO', usuario))
        html=soup

        target= soup.find_all(text=re.compile(r'APELLIDOS'))
        for v in target:
            v.replace_with(v.replace('APELLIDOS', apellido1+' '+apellido2))
        html=soup

        target= soup.find_all(text=re.compile(r'FECHA'))
        for v in target:
            v.replace_with(v.replace('FECHA', str(date.today().strftime('%d-%m-%Y'))))
        html=soup

        target= soup.find_all(text=re.compile(r'FOLIO'))
        for v in target:
            v.replace_with(v.replace('FOLIO', str(folio)))
        html=soup

        target= soup.find_all(text=re.compile(r'TIPO'))
        for v in target:
            v.replace_with(v.replace('TIPO', tipo))
        html=soup

        part1 = MIMEText(text, "plain")
        part2=MIMEText(html.encode('utf-8'), 'html','utf-8')
    
        message['Content-Type'] = "text/html; charset=utf-8"
        message.attach(part1)
        message.attach(part2)
        mailServer = smtplib.SMTP(nombre_smtp , puerto)
        mailServer.starttls()
        mailServer.login(mailaddress , mailpassword)
        try:
            mailto = [mailto]
            mailServer.sendmail(mailaddress, mailto , message.as_string())
            print("\n Enviada la constancia!!!")
            mailServer.quit()
        finally:
            mailServer.close()

    
    def estandar_mail_to(self, subject, mailaddress, mailto, mailbody, mailpassword, nombre_smtp, puerto):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = mailaddress
        message["To"] = mailto
        text = """\ """
        html = '<html lang="es"><body>'+mailbody+'</body></html>'

        part1 = MIMEText(text, "plain")
        part2=MIMEText(html.encode('utf-8'), 'html','utf-8')
    
        message['Content-Type'] = "text/html; charset=utf-8"
        message.attach(part1)
        message.attach(part2)
        mailServer = smtplib.SMTP(nombre_smtp , puerto)
        mailServer.starttls()
        mailServer.login(mailaddress , mailpassword)
        try:
            mailto = [mailto]
            mailServer.sendmail(mailaddress, mailto , message.as_string())
            mailServer.quit()
        finally:
            mailServer.close()


