java -jar ../target/lab_3_4-1.0-SNAPSHOT.jar $1

exit_code=$?

if [ $exit_code -eq 0 ]; then
    wat2wasm ../build/target.wat -o ../build/target.wasm
    node runner.js
fi