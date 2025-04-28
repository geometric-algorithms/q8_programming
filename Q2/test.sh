g++ q2.cpp
for i in {8..9}
do
    echo "========================="
    echo "Running test$i.txt"
    echo "========================="
    ./a.out < "test$i.txt" > "points$i.txt"
    echo
    python3 q2.py test$i.txt points$i.txt
done