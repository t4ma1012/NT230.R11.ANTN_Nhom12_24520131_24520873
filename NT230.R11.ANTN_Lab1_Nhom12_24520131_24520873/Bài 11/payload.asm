bits 64

global true_self_modifying
global encoded_body
global encoded_body_end
global decode_key           ; Cho phép C can thiệp vào khóa giải mã

section .text

true_self_modifying:
    ; 1. LƯU STACK GỐC
    push rbx                
    mov rbx, rsp            

    ; 2. DECODER STUB: Giải mã với khóa động
    lea rsi, [rel encoded_body]
    mov rcx, encoded_body_end - encoded_body
    mov al, [rel decode_key]  ; Lấy khóa ngẫu nhiên do C tạo ra nạp vào AL

.decode_loop:
    xor byte [rsi], al        ; XOR với khóa ngẫu nhiên trong AL
    inc rsi
    loop .decode_loop

    ; 3. TRUE STACK PIVOT
    lea rax, [rel fake_stack_top]
    mov rsp, rax            

    ; 4. ROP CONTROL TRANSFER
    lea rax, [rel encoded_body]
    push rax
    ret                     

section .bss
    align 16
    resq 16                 
    fake_stack_top:

section .data
    align 16
decode_key:
    db 0xAA                 ; Khóa mặc định (sẽ bị Động cơ C ghi đè)
encoded_body:
    ; Chỗ trống 5 bytes. C sẽ tự động mã hóa và bơm payload vào đây mỗi lần chạy
    db 0x00, 0x00, 0x00, 0x00, 0x00  
encoded_body_end:
