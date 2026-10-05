#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/mman.h>
#include <time.h>
#include <stdlib.h>

extern void true_self_modifying(void);
extern unsigned char encoded_body[];
extern unsigned char encoded_body_end[];
extern unsigned char decode_key; // Liên kết với biến khóa trong ASM

static void print_bytes(const char *title, const unsigned char *buf, size_t n) {
    printf("%s", title);
    for (size_t i = 0; i < n; ++i) printf("%02X ", buf[i]);
    putchar('\n');
}

int main(void) {
    // Khởi tạo engine sinh số ngẫu nhiên
    srand(time(NULL));
    // Random khóa XOR từ 1 đến 255
    unsigned char random_key = rand() % 255 + 1; 

    // Opcode gốc: mov rsp, rbx (48 89 DC) | pop rbx (5B) | ret (C3)
    unsigned char original_payload[5] = {0x48, 0x89, 0xDC, 0x5B, 0xC3};

    printf("==================================================\n");
    printf(" TASK 11 - TRUE POLYMORPHIC MUTATION ENGINE DEMO\n");
    printf("==================================================\n\n");

    printf("[*] Mutation Engine Generating New Signature...\n");
    printf("[*] Selected Random XOR Key: 0x%02X\n\n", random_key);

    // GHI ĐÈ KHÓA VÀ PAYLOAD ĐÃ MÃ HÓA VÀO BỘ NHỚ ASM
    decode_key = random_key;
    for (int i = 0; i < 5; i++) {
        encoded_body[i] = original_payload[i] ^ random_key;
    }

    print_bytes("ENCODED PAYLOAD BEFORE : ", encoded_body, 5);

    // Cấp quyền RWX cho vùng nhớ chứa code và biến
    size_t pagesize = sysconf(_SC_PAGE_SIZE);
    uintptr_t page_start = (uintptr_t)&decode_key & ~(pagesize - 1);
    
    if (mprotect((void*)page_start, pagesize, PROT_READ | PROT_WRITE | PROT_EXEC) == -1) {
        perror("mprotect failed");
        return 1;
    }
    printf("[+] Memory protection changed to RWX (Read/Write/Execute) successfully.\n\n");

    printf("Executing true_self_modifying()...\n");
    
    // Kích hoạt ASM giải mã bằng khóa động và bẻ lái Stack Pivot
    true_self_modifying();
    
    printf("CPU executed the decoded payload successfully!\n");
    print_bytes("DECODED PAYLOAD AFTER  : ", encoded_body, 5);
    printf("-> (48 89 DC = mov rsp, rbx | 5B = pop rbx | C3 = ret)\n");

    return 0;
}
