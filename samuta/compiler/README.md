## Требования для запуска
- Java 17
- Gradle (использовать wrapper, который лежит в исходном коде)

## Сборка и запуск
1. Создать jar-архив для проекта:
```bash
./gradlew jar
```

2. Перейти в терминале в папку build/libs

3. Запустить парсер:

```bash
java java -jar compiler-1.0-SNAPSHOT.jar <filename>
```