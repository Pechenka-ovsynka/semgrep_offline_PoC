FROM semgrep/semgrep:1.122.0

COPY ./mock_server /mock_server/ 
# копируем мок сервер
COPY ./sitecustomize.py /usr/lib/python3.12/site-packages/
# грязный хак, чтобы не возиться с сертами
#COPY settings.yml /root/.semgrep/

COPY ./test_file /test_repo
# Копируем тестовый файл с уязвимстью, которая находится только прошным движком (в моке тестовое правило для этого)
RUN cd /test_repo; git init; git add *; git config --global user.email johndoe@example.com; git remote add origin https://fake_repo.com; git commit -m 'Initial project version';
# так как не настоящий репозиторий, то превращаем директорию с тестовым файлом в репозиторий


# в энтрипоинте в hosts добавляется обращеине на локалхост для semgrep.dev, запускается мок сервер, и логин в семгреп через него
COPY ./entrypoint.sh ./

# пример команды 
# CMD source ./entrypoint.sh; cd /test_repo; semgrep ci --pro --sarif --sarif-output=out.sarif
