## Домашнее задание 07 - HTTP сервер

*Задание*: разработать собственный веб-сервер реализующие часть функционала HTTP-протокола.

#### Обязатиельная функциональность сервера:
1. Отвечать 200, 403 или 404 на GET-запросы и HEAD-запросы;
2. Отвечать 405 на прочие запросы;
3. Возвращать файлы по произвольному пути в DOCUMENT_ROOT;
4. Вызов /file.html должен возвращать содердимое DOCUMENT_ROOT/file.html;
5. DOCUMENT_ROOT задается аргументом командной строки -r;
6. Возвращать index.html как индекс директории;
7. Вызов /directory/ должен возвращать DOCUMENT_ROOT/directory/index.html;
8. Отвечать следующими заголовками для успешных GET-запросов: Date, Server, Content-Length, Content-Type, Connection;
9. Корректный Content-Type для: .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf;
10. Понимать пробелы и %XX в именах файлов;
11. Масштабироваться на несколько worker'ов. Числов worker'ов задается аргументом командной строки -w.

#### Проверка работоспособности решения:
1. Корректное отображение страницы в браузере по URL: http://localhost/httptest/wikipedia_russia.html
2. Прохождение набора тестов: https://github.com/s-stupnikov/http-test-suite
3. Результат нагрузочного тесторования Apache Benchmark со следующими параметрами запуска:  ```ab -n 50000 -c 100 -r http://localhost:80/```

#### Описание:
Данный HTTP-сервер отвечает на запросы методов "GET" и "HEAD". Корневая директория со статическими файлами может быть задана через ключ "-r". Обработка множественных запросов к серверу реализована с помощью модуля multiprocessing.

#### Запуск сервера:
Запустить сервер можно двумя способами:
1. Непосредственно на локальной машине с помощью следующей команды: ```python3 httpd.py -w 4```
где по ключу "-w" - задается количество воркеров на сервере;
2. В контейнере Docker:  
Собираем образ:
```bash
docker build -t custom_http . 
```
Из полученного образа создаем и запускам контейнер:
```bash
docker run --name cnt_otus_http -p 80:80 -d custom_http
```

#### Результат:
1. В результате запуска набора тестов командой: 
```python3 httptest.py```
получаем результат из прохождения:
```bash
----------------------------------------------------------------------
Ran 23 tests in 0.023s

OK
```

2. Нагрузочное тестирование Apache Benchmark развернутого в контейнере сервера дало следующий результат:
```bash
ab -n 50000 -c 100 -r http://localhost:80/
This is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        OTUS_HTTP_Server
Server Hostname:        localhost
Server Port:            80

Document Path:          /
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   14.327 seconds                                             
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      7150000 bytes
HTML transferred:       0 bytes
Requests per second:    3489.95 [#/sec] (mean)
Time per request:       28.654 [ms] (mean)
Time per request:       0.287 [ms] (mean, across all concurrent requests)
Transfer rate:          487.37 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       4
Processing:     1   29  40.2     28    1461
Waiting:        1   29  40.2     28    1461
Total:          5   29  40.2     28    1464

Percentage of the requests served within a certain time (ms)
  50%     28
  66%     29
  75%     29
  80%     29
  90%     30
  95%     30
  98%     31
  99%     31
 100%   1464 (longest request)
```