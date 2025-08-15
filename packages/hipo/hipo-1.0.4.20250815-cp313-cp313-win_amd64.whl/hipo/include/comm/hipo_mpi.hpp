
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#ifdef HIPO_MPI_IMPORTS
#define MPI_Init hipo_MPI_Init
#define MPI_Finalize hipo_MPI_Finalize
#define MPI_Initialized hipo_MPI_Initialized
#define MPI_Finalized hipo_MPI_Finalized
#define MPI_Aint hipo_MPI_Aint
#define MPI_Comm hipo_MPI_Comm
#define MPI_Status hipo_MPI_Status
#define MPI_Datatype hipo_MPI_Datatype
#define MPI_Request hipo_MPI_Request
#define MPI_Op hipo_MPI_Op
#define MPI_User_function hipo_MPI_User_function
#define MPI_CHAR hipo_MPI_CHAR
#define MPI_BYTE hipo_MPI_BYTE
#define MPI_INT8_T hipo_MPI_INT8_T
#define MPI_SHORT hipo_MPI_SHORT
#define MPI_SHORT_INT hipo_MPI_SHORT_INT
#define MPI_INT16_T hipo_MPI_INT16_T
#define MPI_INT hipo_MPI_INT
#define MPI_INT32_T hipo_MPI_INT32_T
#define MPI_LONG hipo_MPI_LONG
#define MPI_LONG_INT hipo_MPI_LONG_INT
#define MPI_INT64_T hipo_MPI_INT64_T
#define MPI_FLOAT hipo_MPI_FLOAT
#define MPI_DOUBLE hipo_MPI_DOUBLE
#define MPI_COMPLEX hipo_MPI_COMPLEX
#define MPI_DOUBLE_COMPLEX hipo_MPI_DOUBLE_COMPLEX
#define MPI_SUM hipo_MPI_SUM
#define MPI_MAX hipo_MPI_MAX
#define MPI_MIN hipo_MPI_MIN
#define MPI_COMM_WORLD hipo_MPI_COMM_WORLD
#define MPI_COMM_SELF hipo_MPI_COMM_SELF
#define MPI_IN_INPLACE hipo_MPI_IN_INPLACE
#define MPI_STATUS_IGNORE hipo_MPI_STATUS_IGNORE
#define MPI_STATUSES_IGNORE hipo_MPI_STATUSES_IGNORE
#define MPI_SUCCESS hipo_MPI_SUCCESS
#define MPI_Comm_dup hipo_MPI_Comm_dup
#define MPI_Comm_free hipo_MPI_Comm_free
#define MPI_Comm_size hipo_MPI_Comm_size
#define MPI_Comm_rank hipo_MPI_Comm_rank
#define MPI_Send hipo_MPI_Send
#define MPI_Recv hipo_MPI_Recv
#define MPI_Bcast hipo_MPI_Bcast
#define MPI_Gather hipo_MPI_Gather
#define MPI_Gatherv hipo_MPI_Gatherv
#define MPI_Scatter hipo_MPI_Scatter
#define MPI_Scatterv hipo_MPI_Scatterv
#define MPI_Allgather hipo_MPI_Allgather
#define MPI_Allgatherv hipo_MPI_Allgatherv
#define MPI_Alltoall hipo_MPI_Alltoall
#define MPI_Alltoallv hipo_MPI_Alltoallv
#define MPI_Allreduce hipo_MPI_Allreduce
#define MPI_Isend hipo_MPI_Isend
#define MPI_Irecv hipo_MPI_Irecv
#define MPI_Iallreduce hipo_MPI_Iallreduce
#define MPI_Wait hipo_MPI_Wait
#define MPI_Waitall hipo_MPI_Waitall
#define MPI_Waitsome hipo_MPI_Waitsome
#define MPI_Type_get_extent hipo_MPI_Type_get_extent
#define MPI_Type_contiguous hipo_MPI_Type_contiguous
#define MPI_Type_free hipo_MPI_Type_free
#define MPI_Type_commit hipo_MPI_Type_commit
#define MPI_Op_create hipo_MPI_Op_create
#define MPI_Op_free hipo_MPI_Op_free
#define MPI_Fint hipo_MPI_Fint
#define MPI_Comm_c2f hipo_MPI_Comm_c2f
#define MPI_DATATYPE_NULL hipo_MPI_DATATYPE_NULL
#define MPI_IN_PLACE hipo_MPI_IN_PLACE
#define MPI_REQUEST_NULL hipo_MPI_REQUEST_NULL
#define MPI_Get_processor_name hipo_MPI_Get_processor_name
#define MPI_MAX_PROCESSOR_NAME hipo_MPI_MAX_PROCESSOR_NAME
#define MPI_Group hipo_MPI_Group
#define MPI_Abort hipo_MPI_Abort
#define MPI_Barrier hipo_MPI_Barrier
#define MPI_Comm_create hipo_MPI_Comm_create
#define MPI_Comm_group hipo_MPI_Comm_group
#define MPI_Comm_split hipo_MPI_Comm_split
#define MPI_Get_address hipo_MPI_Get_address
#define MPI_Get_count hipo_MPI_Get_count
#define MPI_Group_free hipo_MPI_Group_free
#define MPI_Group_incl hipo_MPI_Group_incl
#define MPI_Iprobe hipo_MPI_Iprobe
#define MPI_Irsend hipo_MPI_Irsend
#define MPI_Probe hipo_MPI_Probe
#define MPI_Recv_init hipo_MPI_Recv_init
#define MPI_Reduce hipo_MPI_Reduce
#define MPI_Request_free hipo_MPI_Request_free
#define MPI_Scan hipo_MPI_Scan
#define MPI_Send_init hipo_MPI_Send_init
#define MPI_Startall hipo_MPI_Startall
#define MPI_Test hipo_MPI_Test
#define MPI_Testall hipo_MPI_Testall
#define MPI_Type_create_hvector hipo_MPI_Type_create_hvector
#define MPI_Type_create_struct hipo_MPI_Type_create_struct
#define MPI_Type_vector hipo_MPI_Type_vector
#define MPI_Waitany hipo_MPI_Waitany
#define MPI_Wtick hipo_MPI_Wtick
#define MPI_Wtime hipo_MPI_Wtime
#endif
#define hipo_MPI_DATATYPE_NULL hipo_MPI_DATATYPE_NULL_CONST()
#define hipo_MPI_REQUEST_NULL hipo_MPI_REQUEST_NULL_CONST()
#define hipo_MPI_CHAR hipo_MPI_CHAR_CONST()
#define hipo_MPI_BYTE hipo_MPI_BYTE_CONST()
#define hipo_MPI_SHORT hipo_MPI_SHORT_CONST()
#define hipo_MPI_INT hipo_MPI_INT_CONST()
#define hipo_MPI_LONG hipo_MPI_LONG_CONST()
#define hipo_MPI_FLOAT hipo_MPI_FLOAT_CONST()
#define hipo_MPI_DOUBLE hipo_MPI_DOUBLE_CONST()
#define hipo_MPI_LONG_INT hipo_MPI_LONG_INT_CONST()
#define hipo_MPI_SHORT_INT hipo_MPI_SHORT_INT_CONST()
#define hipo_MPI_COMPLEX hipo_MPI_COMPLEX_CONST()
#define hipo_MPI_DOUBLE_COMPLEX hipo_MPI_DOUBLE_COMPLEX_CONST()
#define hipo_MPI_INT8_T hipo_MPI_INT8_T_CONST()
#define hipo_MPI_INT16_T hipo_MPI_INT16_T_CONST()
#define hipo_MPI_INT32_T hipo_MPI_INT32_T_CONST()
#define hipo_MPI_INT64_T hipo_MPI_INT64_T_CONST()
#define hipo_MPI_COMM_WORLD hipo_MPI_COMM_WORLD_CONST()
#define hipo_MPI_COMM_SELF hipo_MPI_COMM_SELF_CONST()
#define hipo_MPI_MAX hipo_MPI_MAX_CONST()
#define hipo_MPI_MIN hipo_MPI_MIN_CONST()
#define hipo_MPI_SUM hipo_MPI_SUM_CONST()
#define hipo_MPI_MAX_PROCESSOR_NAME hipo_MPI_MAX_PROCESSOR_NAME_CONST()
#define hipo_MPI_IN_PLACE hipo_MPI_IN_PLACE_CONST()
#define hipo_MPI_STATUS_IGNORE hipo_MPI_STATUS_IGNORE_CONST()
#define hipo_MPI_STATUSES_IGNORE hipo_MPI_STATUSES_IGNORE_CONST()
#define hipo_MPI_SUCCESS hipo_MPI_SUCCESS_CONST()
typedef void* hipo_MPI_Datatype;
typedef void* hipo_MPI_Comm;
typedef void* hipo_MPI_Group;
typedef void* hipo_MPI_Op;
typedef void* hipo_MPI_Request;
typedef long hipo_MPI_Aint;
typedef int hipo_MPI_Fint;
typedef struct hipo_MPI_Status {  int MPI_SOURCE ; int MPI_TAG ; int MPI_ERROR ; } hipo_MPI_Status;
typedef void ( hipo_MPI_User_function ) ( void * , void * , int * , hipo_MPI_Datatype * );
int hipo_MPI_Allgather ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , hipo_MPI_Comm comm );
int hipo_MPI_Allgatherv ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , const int recvcounts [ ] , const int displs [ ] , hipo_MPI_Datatype recvtype , hipo_MPI_Comm comm );
int hipo_MPI_Allreduce ( const void * sendbuf , void * recvbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op , hipo_MPI_Comm comm );
int hipo_MPI_Alltoall ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , hipo_MPI_Comm comm );
int hipo_MPI_Alltoallv ( const void * sendbuf , const int sendcounts [ ] , const int sdispls [ ] , hipo_MPI_Datatype sendtype , void * recvbuf , const int recvcounts [ ] , const int rdispls [ ] , hipo_MPI_Datatype recvtype , hipo_MPI_Comm comm );
int hipo_MPI_Barrier ( hipo_MPI_Comm comm );
int hipo_MPI_Bcast ( void * buffer , int count , hipo_MPI_Datatype datatype , int root , hipo_MPI_Comm comm );
int hipo_MPI_Gather ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , int root , hipo_MPI_Comm comm );
int hipo_MPI_Gatherv ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , const int recvcounts [ ] , const int displs [ ] , hipo_MPI_Datatype recvtype , int root , hipo_MPI_Comm comm );
int hipo_MPI_Iallreduce ( const void * sendbuf , void * recvbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op , hipo_MPI_Comm comm , hipo_MPI_Request * request );
int hipo_MPI_Reduce ( const void * sendbuf , void * recvbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op , int root , hipo_MPI_Comm comm );
int hipo_MPI_Scan ( const void * sendbuf , void * recvbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op , hipo_MPI_Comm comm );
int hipo_MPI_Scatter ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , int root , hipo_MPI_Comm comm );
int hipo_MPI_Scatterv ( const void * sendbuf , const int sendcounts [ ] , const int displs [ ] , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , int root , hipo_MPI_Comm comm );
int hipo_MPI_Comm_create ( hipo_MPI_Comm comm , hipo_MPI_Group group , hipo_MPI_Comm * newcomm );
int hipo_MPI_Comm_dup ( hipo_MPI_Comm comm , hipo_MPI_Comm * newcomm );
int hipo_MPI_Comm_free ( hipo_MPI_Comm * comm );
int hipo_MPI_Comm_group ( hipo_MPI_Comm comm , hipo_MPI_Group * group );
int hipo_MPI_Comm_rank ( hipo_MPI_Comm comm , int * rank );
int hipo_MPI_Comm_size ( hipo_MPI_Comm comm , int * size );
int hipo_MPI_Comm_split ( hipo_MPI_Comm comm , int color , int key , hipo_MPI_Comm * newcomm );
int hipo_MPI_Get_address ( const void * location , hipo_MPI_Aint * address );
int hipo_MPI_Get_count ( const hipo_MPI_Status * status , hipo_MPI_Datatype datatype , int * count );
int hipo_MPI_Type_commit ( hipo_MPI_Datatype * datatype );
int hipo_MPI_Type_contiguous ( int count , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype );
int hipo_MPI_Type_create_hvector ( int count , int blocklength , hipo_MPI_Aint stride , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype );
int hipo_MPI_Type_create_struct ( int count , const int array_of_blocklengths [ ] , const hipo_MPI_Aint array_of_displacements [ ] , const hipo_MPI_Datatype array_of_types [ ] , hipo_MPI_Datatype * newtype );
int hipo_MPI_Type_free ( hipo_MPI_Datatype * datatype );
int hipo_MPI_Type_get_extent ( hipo_MPI_Datatype datatype , hipo_MPI_Aint * lb , hipo_MPI_Aint * extent );
int hipo_MPI_Type_vector ( int count , int blocklength , int stride , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype );
int hipo_MPI_Group_free ( hipo_MPI_Group * group );
int hipo_MPI_Group_incl ( hipo_MPI_Group group , int n , const int ranks [ ] , hipo_MPI_Group * newgroup );
int hipo_MPI_Abort ( hipo_MPI_Comm comm , int errorcode );
int hipo_MPI_Finalize ( void );
int hipo_MPI_Finalized ( int * flag );
int hipo_MPI_Init ( int * argc , char * * * argv );
int hipo_MPI_Initialized ( int * flag );
int hipo_MPI_Get_processor_name ( char * name , int * resultlen );
int hipo_MPI_Op_create ( hipo_MPI_User_function * user_fn , int commute , hipo_MPI_Op * op );
int hipo_MPI_Op_free ( hipo_MPI_Op * op );
int hipo_MPI_Iprobe ( int source , int tag , hipo_MPI_Comm comm , int * flag , hipo_MPI_Status * status );
int hipo_MPI_Irecv ( void * buf , int count , hipo_MPI_Datatype datatype , int source , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request );
int hipo_MPI_Irsend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request );
int hipo_MPI_Isend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request );
int hipo_MPI_Probe ( int source , int tag , hipo_MPI_Comm comm , hipo_MPI_Status * status );
int hipo_MPI_Recv ( void * buf , int count , hipo_MPI_Datatype datatype , int source , int tag , hipo_MPI_Comm comm , hipo_MPI_Status * status );
int hipo_MPI_Recv_init ( void * buf , int count , hipo_MPI_Datatype datatype , int source , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request );
int hipo_MPI_Send ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm );
int hipo_MPI_Send_init ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request );
int hipo_MPI_Request_free ( hipo_MPI_Request * request );
int hipo_MPI_Startall ( int count , hipo_MPI_Request array_of_requests [ ] );
int hipo_MPI_Test ( hipo_MPI_Request * request , int * flag , hipo_MPI_Status * status );
int hipo_MPI_Testall ( int count , hipo_MPI_Request array_of_requests [ ] , int * flag , hipo_MPI_Status array_of_statuses [ ] );
int hipo_MPI_Wait ( hipo_MPI_Request * request , hipo_MPI_Status * status );
int hipo_MPI_Waitall ( int count , hipo_MPI_Request array_of_requests [ ] , hipo_MPI_Status array_of_statuses [ ] );
int hipo_MPI_Waitany ( int count , hipo_MPI_Request array_of_requests [ ] , int * indx , hipo_MPI_Status * status );
int hipo_MPI_Waitsome ( int incount , hipo_MPI_Request array_of_requests [ ] , int * outcount , int array_of_indices [ ] , hipo_MPI_Status array_of_statuses [ ] );
double hipo_MPI_Wtick ( void );
double hipo_MPI_Wtime ( void );
hipo_MPI_Datatype hipo_MPI_DATATYPE_NULL_CONST();
hipo_MPI_Request hipo_MPI_REQUEST_NULL_CONST();
hipo_MPI_Datatype hipo_MPI_CHAR_CONST();
hipo_MPI_Datatype hipo_MPI_BYTE_CONST();
hipo_MPI_Datatype hipo_MPI_SHORT_CONST();
hipo_MPI_Datatype hipo_MPI_INT_CONST();
hipo_MPI_Datatype hipo_MPI_LONG_CONST();
hipo_MPI_Datatype hipo_MPI_FLOAT_CONST();
hipo_MPI_Datatype hipo_MPI_DOUBLE_CONST();
hipo_MPI_Datatype hipo_MPI_LONG_INT_CONST();
hipo_MPI_Datatype hipo_MPI_SHORT_INT_CONST();
hipo_MPI_Datatype hipo_MPI_COMPLEX_CONST();
hipo_MPI_Datatype hipo_MPI_DOUBLE_COMPLEX_CONST();
hipo_MPI_Datatype hipo_MPI_INT8_T_CONST();
hipo_MPI_Datatype hipo_MPI_INT16_T_CONST();
hipo_MPI_Datatype hipo_MPI_INT32_T_CONST();
hipo_MPI_Datatype hipo_MPI_INT64_T_CONST();
hipo_MPI_Comm hipo_MPI_COMM_WORLD_CONST();
hipo_MPI_Comm hipo_MPI_COMM_SELF_CONST();
hipo_MPI_Op hipo_MPI_MAX_CONST();
hipo_MPI_Op hipo_MPI_MIN_CONST();
hipo_MPI_Op hipo_MPI_SUM_CONST();
int hipo_MPI_MAX_PROCESSOR_NAME_CONST();
void* hipo_MPI_IN_PLACE_CONST();
hipo_MPI_Fint hipo_MPI_Comm_c2f(hipo_MPI_Comm comm);
hipo_MPI_Status* hipo_MPI_STATUS_IGNORE_CONST();
hipo_MPI_Status* hipo_MPI_STATUSES_IGNORE_CONST();
void* hipo_MPI_SUCCESS_CONST();

#ifdef __cplusplus
}
#endif
