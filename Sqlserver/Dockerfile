FROM mcr.microsoft.com/mssql/server:2019-latest


ENV SA_PASSWORD=Mudar@123
ENV ACCEPT_EULA=Y

WORKDIR /tmp


COPY ./tabela/tabela.sql /tmp/


CMD /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P $cd -d master -i /tmp/tabela.sql