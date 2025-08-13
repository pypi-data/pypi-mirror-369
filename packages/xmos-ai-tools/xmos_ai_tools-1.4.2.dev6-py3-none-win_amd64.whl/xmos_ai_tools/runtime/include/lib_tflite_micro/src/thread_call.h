#if !defined(__micro_thread_library_h__)
#define __micro_thread_library_h__

#include <stdint.h>
#ifdef __xcore__
#include <xcore/parallel.h>
#else
typedef unsigned synchronizer_t;
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define XCORE_MAX_NUM_THREADS 5

#ifdef __XC__
    #define UNSAFE unsafe
#else
    #define UNSAFE /**/
#endif

typedef struct { // THIS STRUCT MUST BE IN SYNC WITH ASSEMBLY CODE.
  union {
    uint64_t id_aligned[2]; // Guarantee 64-bit alignment.
    uint32_t id[4];         // Actual IDs
  } thread_ids;             // ids of at most 4 threads - live during invoke
  uint32_t synchroniser;    // synchroniser for threads - live during invoke
} thread_info_t;


#ifndef __XC__

typedef void (*thread_function_pointer_t)(void * arg0, void * arg1, void * arg2);
struct inference_engine;

/** Function that runs the client task
 */
void thread_client(thread_info_t *ptr, int n);

/** Function that runs the client task
 */
static inline void thread_store_sync(thread_info_t *ptr, uint32_t s) {
  ptr->synchroniser = s;
}

/** Function that sets up parameters for one of the client threads
 * This particular one passes the second and third arguments to the thread.
 * When the thread function is actually called (through thread_call)
 * the thread function will be called with those two arguments, 
 * and the first shared argument provided by thread_call.
 * Note - we can make versions with more or fewer parameters.
 * Note - we could pass this function the thread-function itself
 *
 * \param arg1      Second argument for the thread function
 * \param arg2      Third argument for the thread function
 * \param thread_id The thread_id to initialise; one of ptr[0]..ptr[3] above
 */
#ifdef __xcore__
static inline void thread_variable_setup(void * arg1, void * arg2, uint32_t thread_id) {
#ifdef __VX4A__
    asm volatile("xm.tsetr %0, 11, %1" :: "r" (thread_id), "r" (arg1));
    asm volatile("xm.tsetr %0, 12, %1" :: "r" (thread_id), "r" (arg2));
    asm volatile("xm.tsetr %0, 24, %1" :: "r" (thread_id), "r" (1));
#else
    asm volatile("set t[%0]:r1, %1" :: "r" (thread_id), "r" (arg1));
    asm volatile("set t[%0]:r2, %1" :: "r" (thread_id), "r" (arg2));
    asm volatile("set t[%0]:r10, %1" :: "r" (thread_id), "r" (1));
#endif
}
#else
extern void thread_variable_setup(void * arg1, void * arg2, uint32_t thread_id);
#endif

/** Function that starts all thread functions and runs them until completion.
 * It is assumed that the variable parts have been set up per thread.
 * by thread_variable_setup.
 * This thread will also invoke the function with the given variable arguments.
 *
 * \param arg0      First argument shared among all threads (usually the output pointer)
 * \param arg1      Second argument for the master thread function
 * \param arg2      Third argument for the master thread function
 * \param fp        thread function to call on all threads.
 * \param ptr       Pointer to the thread info block held in the xcore
 * interpreter.
 */
void thread_call(void * arg0, void * arg1, void * arg2,
                 thread_function_pointer_t fp, thread_info_t *ptr);
#ifdef __cplusplus
};
#endif

#endif // __XC__

#endif // __micro_thread_library_h__
