# Билд грамматики в TypeScript
brew install antlr
mkdir ./compiler/Variant15
antlr4 -Dlanguage=TypeScript -o ./compiler/Variant15 ./grammar/Variant15.g4


#Установка зависимостей
cd ./compiler
npm install


#Jasmin - ассемблер
brew install jasmin


#Запуск системы
npm run dev