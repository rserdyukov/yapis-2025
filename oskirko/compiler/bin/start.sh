java -jar ../target/lab_3_4-1.0-SNAPSHOT.jar $1
wat2wasm ../build/target.wat -o ../build/target.wasm
node runner.js