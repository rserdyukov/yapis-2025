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
@.str2 = private unnamed_addr constant [15 x i8] c"alice@mail.com\00"
@.str3 = private unnamed_addr constant [4 x i8] c"Bob\00"
@.str4 = private unnamed_addr constant [13 x i8] c"bob@mail.com\00"
@.str5 = private unnamed_addr constant [8 x i8] c"Charlie\00"
@.str6 = private unnamed_addr constant [17 x i8] c"charlie@mail.com\00"
@.str7 = private unnamed_addr constant [1 x i8] c"\00"
@.str8 = private unnamed_addr constant [20 x i8] c"charlie@newmail.com\00"
@.str9 = private unnamed_addr constant [57 x i8] c"Актуальные данные по клиентам:\00"
@.str10 = private unnamed_addr constant [121 x i8] c"id | name | email | balance\0A---------------------------\0A1 | Alice | alice@mail.com | 100.0\0A2 | Bob | bob@mail.com | 75.5\00"


define i32 @main() {
entry:
  %t1 = alloca i8*
  %t2 = alloca i32
  %t12 = alloca i8*
  %t43 = alloca i8*
  store i8* null, i8** %t1
  store i32 0, i32* %t2
  %t3 = load i32, i32* %t2
  %t4 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  %t5 = getelementptr inbounds [15 x i8], [15 x i8]* @.str2, i32 0, i32 0
  %t6 = load i32, i32* %t2
  %t7 = getelementptr inbounds [4 x i8], [4 x i8]* @.str3, i32 0, i32 0
  %t8 = getelementptr inbounds [13 x i8], [13 x i8]* @.str4, i32 0, i32 0
  %t9 = load i32, i32* %t2
  %t10 = getelementptr inbounds [8 x i8], [8 x i8]* @.str5, i32 0, i32 0
  %t11 = getelementptr inbounds [17 x i8], [17 x i8]* @.str6, i32 0, i32 0
  %t13 = alloca i32
  store i32 0, i32* %t13
  br label %label2
label2:
  %t14 = load i32, i32* %t13
  %t15 = icmp ult i32 %t14, 3
  br i1 %t15, label %label3, label %label5
label3:
  %t16 = load i8*, i8** %t1
  %t17 = load i32, i32* %t13
  %t18 = load i32, i32* %t13
  switch i32 %t18, label %label11 [
    i32 0, label %label8
    i32 1, label %label9
    i32 2, label %label10
  ]
label8:
  %t21 = getelementptr inbounds [6 x i8], [6 x i8]* @.str1, i32 0, i32 0
  br label %label7
label9:
  %t23 = getelementptr inbounds [4 x i8], [4 x i8]* @.str3, i32 0, i32 0
  br label %label7
label10:
  %t25 = getelementptr inbounds [8 x i8], [8 x i8]* @.str5, i32 0, i32 0
  br label %label7
label11:
  %t27 = getelementptr inbounds [1 x i8], [1 x i8]* @.str7, i32 0, i32 0
  br label %label7
label7:
  %t28 = phi i8* [%t21, %label8], [%t23, %label9], [%t25, %label10], [%t27, %label11]
  %t29 = getelementptr inbounds [4 x i8], [4 x i8]* @.str3, i32 0, i32 0
  %t30 = call i32 @strcmp(i8* %t28, i8* %t29)
  %t31 = icmp eq i32 %t30, 0
  %t32 = load i32, i32* %t13
  %t33 = load i32, i32* %t13
  switch i32 %t33, label %label16 [
    i32 0, label %label13
    i32 1, label %label14
    i32 2, label %label15
  ]
label13:
  %t35 = fadd double 0.0, 100.0
  br label %label12
label14:
  %t36 = fadd double 0.0, 50.5
  br label %label12
label15:
  %t37 = fadd double 0.0, 0.0
  br label %label12
label16:
  %t38 = fadd double 0.0, 0.0
  br label %label12
label12:
  %t39 = phi double [%t35, %label13], [%t36, %label14], [%t37, %label15], [%t38, %label16]
  %t40 = fadd double %t39, 25.0
  br label %label4
label4:
  %t41 = load i32, i32* %t13
  %t42 = add i32 %t41, 1
  store i32 %t42, i32* %t13
  br label %label2
label5:
  %t44 = alloca i32
  store i32 0, i32* %t44
  br label %label18
label18:
  %t45 = load i32, i32* %t44
  %t46 = icmp ult i32 %t45, 3
  br i1 %t46, label %label19, label %label21
label19:
  %t47 = load i8*, i8** %t1
  %t48 = load i32, i32* %t44
  %t49 = load i32, i32* %t44
  switch i32 %t49, label %label27 [
    i32 0, label %label24
    i32 1, label %label25
    i32 2, label %label26
  ]
label24:
  %t51 = add i32 0, 1
  br label %label23
label25:
  %t52 = add i32 0, 2
  br label %label23
label26:
  %t53 = add i32 0, 3
  br label %label23
label27:
  %t54 = add i32 0, 0
  br label %label23
label23:
  %t55 = phi i32 [%t51, %label24], [%t52, %label25], [%t53, %label26], [%t54, %label27]
  %t56 = icmp eq i32 %t55, 3
  %t57 = icmp eq i32 %t55, 3
  br i1 %t57, label %label28, label %label20
label28:
  %t58 = getelementptr inbounds [20 x i8], [20 x i8]* @.str8, i32 0, i32 0
  br label %label20
label20:
  %t59 = load i32, i32* %t44
  %t60 = add i32 %t59, 1
  store i32 %t60, i32* %t44
  br label %label18
label21:
  %t61 = getelementptr inbounds [31 x i8], [31 x i8]* @.str9, i32 0, i32 0
  call i32 @puts(i8* %t61)
  %t62 = load i8*, i8** %t1
  %t63 = getelementptr inbounds [121 x i8], [121 x i8]* @.str10, i32 0, i32 0
  call i32 @puts(i8* %t63)
  ret i32 0
}