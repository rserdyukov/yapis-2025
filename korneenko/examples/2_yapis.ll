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
@.str2 = private unnamed_addr constant [4 x i8] c"new\00"
@.str3 = private unnamed_addr constant [4 x i8] c"Bob\00"
@.str4 = private unnamed_addr constant [8 x i8] c"shipped\00"
@.str5 = private unnamed_addr constant [8 x i8] c"Charlie\00"
@.str6 = private unnamed_addr constant [10 x i8] c"cancelled\00"
@.str7 = private unnamed_addr constant [11 x i8] c"processing\00"
@.str8 = private unnamed_addr constant [40 x i8] c"Статус по заказам Alice:\00"
@.str9 = private unnamed_addr constant [1 x i8] c"\00"
@.str10 = private unnamed_addr constant [13 x i8] c"Заказ #\00"
@.str11 = private unnamed_addr constant [3 x i8] c"%d\00"
@.str12 = private unnamed_addr constant [6 x i8] c" — \00"
@.str13 = private unnamed_addr constant [15 x i8] c", сумма: \00"
@.str14 = private unnamed_addr constant [5 x i8] c"%.2f\00"
@.str15 = private unnamed_addr constant [39 x i8] c"Общая сумма заказов: \00"


define i8* @get_order_summary(i8* %0, i8* %1) {
entry:
  %t23 = alloca i8*
  store i8* %0, i8** %t23
  %t24 = alloca i8*
  store i8* %1, i8** %t24
  %t25 = alloca double
  %t26 = alloca i8*
  %t60 = alloca i32
  %t129 = alloca i32
  store double 0.0, double* %t25
  %t27 = alloca i32
  store i32 0, i32* %t27
  br label %label2
label2:
  %t28 = load i32, i32* %t27
  %t29 = icmp ult i32 %t28, 4
  br i1 %t29, label %label3, label %label5
label3:
  %t30 = load i8*, i8** %t23
  %t31 = load i32, i32* %t27
  %t32 = load i32, i32* %t27
  switch i32 %t32, label %label15 [
    i32 0, label %label11
    i32 1, label %label12
    i32 2, label %label13
    i32 3, label %label14
  ]
label11:
  %t35 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  br label %label10
label12:
  %t37 = getelementptr inbounds [4 x i8], [4 x i8]* @.str3, i32 0, i32 0
  br label %label10
label13:
  %t39 = getelementptr inbounds [8 x i8], [8 x i8]* @.str5, i32 0, i32 0
  br label %label10
label14:
  %t41 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  br label %label10
label15:
  %t43 = getelementptr inbounds [1 x i8], [1 x i8]* @.str9, i32 0, i32 0
  br label %label10
label10:
  %t44 = phi i8* [%t35, %label11], [%t37, %label12], [%t39, %label13], [%t41, %label14], [%t43, %label15]
  %t45 = load i8*, i8** %t24
  %t46 = call i32 @strcmp(i8* %t44, i8* %t45)
  %t47 = icmp eq i32 %t46, 0
  br i1 %t47, label %label7, label %label8
label7:
  %t48 = load double, double* %t25
  %t49 = load i32, i32* %t27
  %t50 = load i32, i32* %t27
  switch i32 %t50, label %label21 [
    i32 0, label %label17
    i32 1, label %label18
    i32 2, label %label19
    i32 3, label %label20
  ]
label17:
  %t52 = fadd double 0.0, 250.0
  br label %label16
label18:
  %t53 = fadd double 0.0, 150.0
  br label %label16
label19:
  %t54 = fadd double 0.0, 500.0
  br label %label16
label20:
  %t55 = fadd double 0.0, 100.0
  br label %label16
label21:
  %t56 = fadd double 0.0, 0.0
  br label %label16
label16:
  %t57 = phi double [%t52, %label17], [%t53, %label18], [%t54, %label19], [%t55, %label20], [%t56, %label21]
  %t58 = fadd double %t48, %t57
  store double %t58, double* %t25
  %t59 = getelementptr inbounds [8 x i8], [8 x i8]* @.str10, i32 0, i32 0
  store i32 0, i32* %t60
  %t61 = load i32, i32* %t60
  %t62 = load i32, i32* %t27
  %t63 = load i32, i32* %t27
  switch i32 %t63, label %label27 [
    i32 0, label %label23
    i32 1, label %label24
    i32 2, label %label25
    i32 3, label %label26
  ]
label23:
  %t65 = add i32 0, 1
  br label %label22
label24:
  %t66 = add i32 0, 2
  br label %label22
label25:
  %t67 = add i32 0, 3
  br label %label22
label26:
  %t68 = add i32 0, 4
  br label %label22
label27:
  %t69 = add i32 0, 0
  br label %label22
label22:
  %t70 = phi i32 [%t65, %label23], [%t66, %label24], [%t67, %label25], [%t68, %label26], [%t69, %label27]
  %t71 = call i8* @malloc(i64 32)
  %t72 = getelementptr inbounds [3 x i8], [3 x i8]* @.str11, i32 0, i32 0
  call i32 (i8*, i8*, ...) @sprintf(i8* %t71, i8* %t72, i32 %t70)
  %t73 = call i64 @strlen(i8* %t59)
  %t74 = call i64 @strlen(i8* %t71)
  %t76 = add i64 %t73, %t74
  %t75 = add i64 %t76, 1
  %t77 = call i8* @malloc(i64 %t75)
  call i8* @strcpy(i8* %t77, i8* %t59)
  call i8* @strcat(i8* %t77, i8* %t71)
  %t78 = getelementptr inbounds [4 x i8], [4 x i8]* @.str12, i32 0, i32 0
  %t79 = call i64 @strlen(i8* %t77)
  %t80 = call i64 @strlen(i8* %t78)
  %t82 = add i64 %t79, %t80
  %t81 = add i64 %t82, 1
  %t83 = call i8* @malloc(i64 %t81)
  call i8* @strcpy(i8* %t83, i8* %t77)
  call i8* @strcat(i8* %t83, i8* %t78)
  %t84 = load i32, i32* %t27
  %t85 = load i32, i32* %t27
  switch i32 %t85, label %label33 [
    i32 0, label %label29
    i32 1, label %label30
    i32 2, label %label31
    i32 3, label %label32
  ]
label29:
  %t88 = getelementptr inbounds [4 x i8], [4 x i8]* @.str2, i32 0, i32 0
  br label %label28
label30:
  %t90 = getelementptr inbounds [8 x i8], [8 x i8]* @.str4, i32 0, i32 0
  br label %label28
label31:
  %t92 = getelementptr inbounds [10 x i8], [10 x i8]* @.str6, i32 0, i32 0
  br label %label28
label32:
  %t94 = getelementptr inbounds [11 x i8], [11 x i8]* @.str7, i32 0, i32 0
  br label %label28
label33:
  %t96 = getelementptr inbounds [1 x i8], [1 x i8]* @.str9, i32 0, i32 0
  br label %label28
label28:
  %t97 = phi i8* [%t88, %label29], [%t90, %label30], [%t92, %label31], [%t94, %label32], [%t96, %label33]
  %t98 = call i64 @strlen(i8* %t83)
  %t99 = call i64 @strlen(i8* %t97)
  %t101 = add i64 %t98, %t99
  %t100 = add i64 %t101, 1
  %t102 = call i8* @malloc(i64 %t100)
  call i8* @strcpy(i8* %t102, i8* %t83)
  call i8* @strcat(i8* %t102, i8* %t97)
  %t103 = getelementptr inbounds [10 x i8], [10 x i8]* @.str13, i32 0, i32 0
  %t104 = call i64 @strlen(i8* %t102)
  %t105 = call i64 @strlen(i8* %t103)
  %t107 = add i64 %t104, %t105
  %t106 = add i64 %t107, 1
  %t108 = call i8* @malloc(i64 %t106)
  call i8* @strcpy(i8* %t108, i8* %t102)
  call i8* @strcat(i8* %t108, i8* %t103)
  %t109 = load i32, i32* %t60
  %t110 = load i32, i32* %t27
  %t111 = load i32, i32* %t27
  switch i32 %t111, label %label39 [
    i32 0, label %label35
    i32 1, label %label36
    i32 2, label %label37
    i32 3, label %label38
  ]
label35:
  %t113 = fadd double 0.0, 250.0
  br label %label34
label36:
  %t114 = fadd double 0.0, 150.0
  br label %label34
label37:
  %t115 = fadd double 0.0, 500.0
  br label %label34
label38:
  %t116 = fadd double 0.0, 100.0
  br label %label34
label39:
  %t117 = fadd double 0.0, 0.0
  br label %label34
label34:
  %t118 = phi double [%t113, %label35], [%t114, %label36], [%t115, %label37], [%t116, %label38], [%t117, %label39]
  %t119 = call i8* @malloc(i64 32)
  %t120 = getelementptr inbounds [5 x i8], [5 x i8]* @.str14, i32 0, i32 0
  call i32 (i8*, i8*, ...) @sprintf(i8* %t119, i8* %t120, double %t118)
  %t121 = call i64 @strlen(i8* %t108)
  %t122 = call i64 @strlen(i8* %t119)
  %t124 = add i64 %t121, %t122
  %t123 = add i64 %t124, 1
  %t125 = call i8* @malloc(i64 %t123)
  call i8* @strcpy(i8* %t125, i8* %t108)
  call i8* @strcat(i8* %t125, i8* %t119)
  call i32 @puts(i8* %t125)
  br label %label9
label8:
  br label %label9
label9:
  br label %label4
label4:
  %t126 = load i32, i32* %t27
  %t127 = add i32 %t126, 1
  store i32 %t127, i32* %t27
  br label %label2
label5:
  %t128 = getelementptr inbounds [22 x i8], [22 x i8]* @.str15, i32 0, i32 0
  store i32 0, i32* %t129
  %t130 = load i32, i32* %t129
  %t131 = load double, double* %t25
  %t132 = call i8* @malloc(i64 32)
  %t133 = getelementptr inbounds [5 x i8], [5 x i8]* @.str14, i32 0, i32 0
  call i32 (i8*, i8*, ...) @sprintf(i8* %t132, i8* %t133, double %t131)
  %t134 = call i64 @strlen(i8* %t128)
  %t135 = call i64 @strlen(i8* %t132)
  %t137 = add i64 %t134, %t135
  %t136 = add i64 %t137, 1
  %t138 = call i8* @malloc(i64 %t136)
  call i8* @strcpy(i8* %t138, i8* %t128)
  call i8* @strcat(i8* %t138, i8* %t132)
  ret i8* %t138
}

define i32 @main() {
entry:
  %t1 = alloca i8*
  %t2 = alloca i32
  %t15 = alloca i32
  %t20 = alloca i8*
  store i8* null, i8** %t1
  store i32 0, i32* %t2
  %t3 = load i32, i32* %t2
  %t4 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  %t5 = getelementptr inbounds [4 x i8], [4 x i8]* @.str2, i32 0, i32 0
  %t6 = load i32, i32* %t2
  %t7 = getelementptr inbounds [4 x i8], [4 x i8]* @.str3, i32 0, i32 0
  %t8 = getelementptr inbounds [8 x i8], [8 x i8]* @.str4, i32 0, i32 0
  %t9 = load i32, i32* %t2
  %t10 = getelementptr inbounds [8 x i8], [8 x i8]* @.str5, i32 0, i32 0
  %t11 = getelementptr inbounds [10 x i8], [10 x i8]* @.str6, i32 0, i32 0
  %t12 = load i32, i32* %t2
  %t13 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  %t14 = getelementptr inbounds [11 x i8], [11 x i8]* @.str7, i32 0, i32 0
  store i32 0, i32* %t15
  %t16 = load i32, i32* %t15
  %t17 = load i8*, i8** %t1
  %t18 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  %t19 = call i8* @get_order_summary(i8* %t17, i8* %t18)
  store i8* %t19, i8** %t20
  %t21 = getelementptr inbounds [25 x i8], [25 x i8]* @.str8, i32 0, i32 0
  call i32 @puts(i8* %t21)
  %t22 = load i8*, i8** %t20
  call i32 @puts(i8* %t22)
  ret i32 0
}