python ../vpp+.py adder.vpp WIDTH=8 > adder.new
python ../vpp+.py mux.vpp PORTS=4 WIDTH=8 > mux.new
python ../vpp+.py recurse.vpp > recurse.new
python ../vpp+.py macro.vpp > macro.new

for TEST in adder mux recurse macro
do
    diff -w $TEST.v $TEST.new
    rc=$?
    if [[ $rc != 0 ]] ; then
        echo "Regress failed"
        exit $rc
    fi
done

rm *.new