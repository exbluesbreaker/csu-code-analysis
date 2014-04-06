#!/bin/bash

print_help() {
  echo "This is Java static analysis tools from CSU. Here you can:"
  echo " * generate abstract syntax tree (AST)"
  echo " * generate universal class representation (UCR)"
  echo " * generate control-flow graph (CFG)"
  echo
  echo "If you want to work with some of these analisys you should use appropriate mode-parameter:"
  echo "- ast for AST"
  echo "- ucr for UCR"
  echo "- ucfr for UCFR"
  echo "USAGE: <mode-parameter> [<param1>..]"
  echo
  echo "For example:"
  echo "$ ./tools.sh ast ~/my_project/src user/ast.xml"
  echo "will generate AST for project located at '~/my_project/src' and write result to 'user/ast.xml' file."
  echo
  echo "Follow the instructions in each mode by running it without parameters."
}

if [ ! -d ./build ] || [ ! -f ./build/jxmlgen.jar ] || [ ! -f ./build/jclassgen.jar ] || [ ! -f ./build/jcfgen.jar ] ; then
  echo "ERROR! Project should be built first."
  echo "To do this, use ant"
  exit 1
fi

case $1 in
  ast)
    java -jar build/jxmlgen.jar $2 $3
    ;;
  ucr)
    java -jar build/jclassgen.jar $2 $3
    ;;
  ucfr)
    java -jar build/jcfgen.jar $2 $3 $4
    ;;
  help)
    print_help
    ;;
  *)
  print_help
  ;;
esac

