; Модуль LLVM IR, сгенерированный из GSL1
declare i32 @printf(i8*, ...)
declare i32 @puts(i8*)
declare i8* @malloc(i64)
declare i8* @strcpy(i8*, i8*)
declare i8* @strcat(i8*, i8*)
declare i64 @strlen(i8*)
declare i32 @sprintf(i8*, i8*, ...)
declare i32 @strcmp(i8*, i8*)

; Модуль LLVM IR, сгенерированный из GSL1

@.str1 = private unnamed_addr constant [6 x i8] c"Alice\00"
@.str2 = private unnamed_addr constant [3 x i8] c"IT\00"
@.str3 = private unnamed_addr constant [4 x i8] c"Bob\00"
@.str4 = private unnamed_addr constant [6 x i8] c"Sales\00"
@.str5 = private unnamed_addr constant [8 x i8] c"Charlie\00"
@.str6 = private unnamed_addr constant [6 x i8] c"David\00"
@.str7 = private unnamed_addr constant [3 x i8] c"HR\00"
@.str8 = private unnamed_addr constant [38 x i8] c"Сотрудники младше 30:\00"
@.str9 = private unnamed_addr constant [21 x i8] c"Сотрудник: \00"
@.str10 = private unnamed_addr constant [1 x i8] c"\00"
@.str11 = private unnamed_addr constant [19 x i8] c", возраст: \00"
@.str12 = private unnamed_addr constant [3 x i8] c"%d\00"
@.str13 = private unnamed_addr constant [48 x i8] c"Всего сотрудников младше \00"
@.str14 = private unnamed_addr constant [3 x i8] c": \00"


define i8* @get_young_employees(i8* %0, i32 %1) {
entry:
  %t22 = alloca i8*
  store i8* %0, i8** %t22
  %t23 = alloca i32
  store i32 %1, i32* %t23
  %t24 = alloca i32
  %t25 = alloca i8*
  %t70 = alloca i32
  %t91 = alloca i32
  store i32 0, i32* %t24
  %t26 = alloca i32
  store i32 0, i32* %t26
  br label %label2
label2:
  %t27 = load i32, i32* %t26
  %t28 = icmp ult i32 %t27, 4
  br i1 %t28, label %label3, label %label5
label3:
  %t29 = load i8*, i8** %t22
  %t30 = load i32, i32* %t26
  %t31 = load i32, i32* %t26
  switch i32 %t31, label %label15 [
    i32 0, label %label11
    i32 1, label %label12
    i32 2, label %label13
    i32 3, label %label14
  ]
label11:
  %t33 = add i32 0, 25
  br label %label10
label12:
  %t34 = add i32 0, 30
  br label %label10
label13:
  %t35 = add i32 0, 28
  br label %label10
label14:
  %t36 = add i32 0, 35
  br label %label10
label15:
  %t37 = add i32 0, 0
  br label %label10
label10:
  %t38 = phi i32 [%t33, %label11], [%t34, %label12], [%t35, %label13], [%t36, %label14], [%t37, %label15]
  %t39 = load i32, i32* %t23
  %t40 = icmp slt i32 %t38, %t39
  %t41 = icmp slt i32 %t38, %t39
  br i1 %t41, label %label7, label %label8
label7:
  %t42 = load i32, i32* %t24
  %t43 = add i32 %t42, 1
  store i32 %t43, i32* %t24
  %t44 = getelementptr inbounds [12 x i8], [12 x i8]* @.str9, i32 0, i32 0
  %t45 = load i32, i32* %t26
  %t46 = load i32, i32* %t26
  switch i32 %t46, label %label21 [
    i32 0, label %label17
    i32 1, label %label18
    i32 2, label %label19
    i32 3, label %label20
  ]
label17:
  %t49 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  br label %label16
label18:
  %t51 = getelementptr inbounds [4 x i8], [4 x i8]* @.str3, i32 0, i32 0
  br label %label16
label19:
  %t53 = getelementptr inbounds [8 x i8], [8 x i8]* @.str5, i32 0, i32 0
  br label %label16
label20:
  %t55 = getelementptr inbounds [6 x i8], [6 x i8]* @.str6, i32 0, i32 0
  br label %label16
label21:
  %t57 = getelementptr inbounds [1 x i8], [1 x i8]* @.str10, i32 0, i32 0
  br label %label16
label16:
  %t58 = phi i8* [%t49, %label17], [%t51, %label18], [%t53, %label19], [%t55, %label20], [%t57, %label21]
  %t59 = call i64 @strlen(i8* %t44)
  %t60 = call i64 @strlen(i8* %t58)
  %t62 = add i64 %t59, %t60
  %t61 = add i64 %t62, 1
  %t63 = call i8* @malloc(i64 %t61)
  call i8* @strcpy(i8* %t63, i8* %t44)
  call i8* @strcat(i8* %t63, i8* %t58)
  %t64 = getelementptr inbounds [12 x i8], [12 x i8]* @.str11, i32 0, i32 0
  %t65 = call i64 @strlen(i8* %t63)
  %t66 = call i64 @strlen(i8* %t64)
  %t68 = add i64 %t65, %t66
  %t67 = add i64 %t68, 1
  %t69 = call i8* @malloc(i64 %t67)
  call i8* @strcpy(i8* %t69, i8* %t63)
  call i8* @strcat(i8* %t69, i8* %t64)
  store i32 0, i32* %t70
  %t71 = load i32, i32* %t70
  %t72 = load i32, i32* %t26
  %t73 = load i32, i32* %t26
  switch i32 %t73, label %label27 [
    i32 0, label %label23
    i32 1, label %label24
    i32 2, label %label25
    i32 3, label %label26
  ]
label23:
  %t75 = add i32 0, 25
  br label %label22
label24:
  %t76 = add i32 0, 30
  br label %label22
label25:
  %t77 = add i32 0, 28
  br label %label22
label26:
  %t78 = add i32 0, 35
  br label %label22
label27:
  %t79 = add i32 0, 0
  br label %label22
label22:
  %t80 = phi i32 [%t75, %label23], [%t76, %label24], [%t77, %label25], [%t78, %label26], [%t79, %label27]
  %t81 = call i8* @malloc(i64 32)
  %t82 = getelementptr inbounds [3 x i8], [3 x i8]* @.str12, i32 0, i32 0
  call i32 (i8*, i8*, ...) @sprintf(i8* %t81, i8* %t82, i32 %t80)
  %t83 = call i64 @strlen(i8* %t69)
  %t84 = call i64 @strlen(i8* %t81)
  %t86 = add i64 %t83, %t84
  %t85 = add i64 %t86, 1
  %t87 = call i8* @malloc(i64 %t85)
  call i8* @strcpy(i8* %t87, i8* %t69)
  call i8* @strcat(i8* %t87, i8* %t81)
  call i32 @puts(i8* %t87)
  br label %label9
label8:
  br label %label9
label9:
  br label %label4
label4:
  %t88 = load i32, i32* %t26
  %t89 = add i32 %t88, 1
  store i32 %t89, i32* %t26
  br label %label2
label5:
  %t90 = getelementptr inbounds [26 x i8], [26 x i8]* @.str13, i32 0, i32 0
  store i32 0, i32* %t91
  %t92 = load i32, i32* %t91
  %t93 = load i32, i32* %t23
  %t94 = call i8* @malloc(i64 32)
  %t95 = getelementptr inbounds [3 x i8], [3 x i8]* @.str12, i32 0, i32 0
  call i32 (i8*, i8*, ...) @sprintf(i8* %t94, i8* %t95, i32 %t93)
  %t96 = call i64 @strlen(i8* %t90)
  %t97 = call i64 @strlen(i8* %t94)
  %t99 = add i64 %t96, %t97
  %t98 = add i64 %t99, 1
  %t100 = call i8* @malloc(i64 %t98)
  call i8* @strcpy(i8* %t100, i8* %t90)
  call i8* @strcat(i8* %t100, i8* %t94)
  %t101 = getelementptr inbounds [3 x i8], [3 x i8]* @.str14, i32 0, i32 0
  %t102 = call i64 @strlen(i8* %t100)
  %t103 = call i64 @strlen(i8* %t101)
  %t105 = add i64 %t102, %t103
  %t104 = add i64 %t105, 1
  %t106 = call i8* @malloc(i64 %t104)
  call i8* @strcpy(i8* %t106, i8* %t100)
  call i8* @strcat(i8* %t106, i8* %t101)
  %t107 = load i32, i32* %t91
  %t108 = load i32, i32* %t24
  %t109 = call i8* @malloc(i64 32)
  %t110 = getelementptr inbounds [3 x i8], [3 x i8]* @.str12, i32 0, i32 0
  call i32 (i8*, i8*, ...) @sprintf(i8* %t109, i8* %t110, i32 %t108)
  %t111 = call i64 @strlen(i8* %t106)
  %t112 = call i64 @strlen(i8* %t109)
  %t114 = add i64 %t111, %t112
  %t113 = add i64 %t114, 1
  %t115 = call i8* @malloc(i64 %t113)
  call i8* @strcpy(i8* %t115, i8* %t106)
  call i8* @strcat(i8* %t115, i8* %t109)
  ret i8* %t115
}

define i32 @main() {
entry:
  %t1 = alloca i8*
  %t2 = alloca i32
  %t15 = alloca i32
  %t19 = alloca i8*
  store i8* null, i8** %t1
  store i32 0, i32* %t2
  %t3 = load i32, i32* %t2
  %t4 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  %t5 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  %t6 = load i32, i32* %t2
  %t7 = getelementptr inbounds [4 x i8], [4 x i8]* @.str3, i32 0, i32 0
  %t8 = getelementptr inbounds [6 x i8], [6 x i8]* @.str4, i32 0, i32 0
  %t9 = load i32, i32* %t2
  %t10 = getelementptr inbounds [8 x i8], [8 x i8]* @.str5, i32 0, i32 0
  %t11 = getelementptr inbounds [3 x i8], [3 x i8]* @.str2, i32 0, i32 0
  %t12 = load i32, i32* %t2
  %t13 = getelementptr inbounds [6 x i8], [6 x i8]* @.str6, i32 0, i32 0
  %t14 = getelementptr inbounds [3 x i8], [3 x i8]* @.str7, i32 0, i32 0
  store i32 0, i32* %t15
  %t16 = load i32, i32* %t15
  %t17 = load i8*, i8** %t1
  %t18 = call i8* @get_young_employees(i8* %t17, i32 30)
  store i8* %t18, i8** %t19
  %t20 = getelementptr inbounds [22 x i8], [22 x i8]* @.str8, i32 0, i32 0
  call i32 @puts(i8* %t20)
  %t21 = load i8*, i8** %t19
  call i32 @puts(i8* %t21)
  ret i32 0
}