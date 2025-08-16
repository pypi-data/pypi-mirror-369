! Compiled subroutines for the Enhanced Multi-Block Solve
! These are compiled with Python interfaces using f2py
! and then called from the main program which deals with
! fiddly bits like block patching and boundary conditions
module ember

    implicit none

contains

    include 'indexing.f90'
    include 'distribute.f90'
    include 'operators.f90'
    include 'smooth.f90'
    include 'viscous.f90'
    include 'fluxes.f90'
    include 'multigrid.f90'
    include 'matmul.f90'

    ! Using the current flow field, calculate changes to conserved
    ! variables that advance each cell in time. Specifically,
    ! 1) Evaluate fluxes of conserved quantities across each face
    ! 2) Sum fluxes into each cell
    ! 3) Add on body forces and source terms (defined per unit vol)
    ! 4) The net flow and body force for each cell is the 'residual' of
    !    the conservation equations:
    !       resid = vol * d(cons)/dt = flux_net + source * vol
    !    The change in the conserved variables is given by integrating
    !    forward in time:
    !       d(cons) = resid * dt / vol = (flux_net/vol + source) * dt
    !
    subroutine residual(&
        fb, &              ! Flow properties and body force
        dt_vol, &
        fsum, &
        ijk_mg, fmgrid, &                     ! Multigrid indexing and factor
        fdamp, &                              ! Damping factor
        resid_cell, &                              ! Cell residual out
        resid_node, &                          ! Previous residual out
        ischeme, &
        ni, nj, nk, nmg &  ! Numbers of points dummy args
        )

        ! Number of conserved variables nv = 5
        ! Number of coordinate directions nc = 3
        ! Have to use magic numbers or f2py thinks they should be dummy args

        ! Cell body force per unit volume (and potential mass/energy sources)
        real, intent (in) :: fb   (ni-1, nj-1, nk-1, 5)

        ! Cell areas, volumes, time steps
        real, intent (in)  :: dt_vol(ni-1, nj-1, nk-1, nmg)

        ! Multigrid indices
        integer*2, intent (in) :: ijk_mg(3, ni-1, nj-1, nk-1, nmg-1)

        ! Cell residual out
        real, intent (inout) :: resid_cell(ni-1, nj-1, nk-1, 5, 2)
        real, intent (inout) :: resid_node(ni, nj, nk, 5)

        ! Numbers of points dummy args
        integer, intent (in)  :: ni
        integer, intent (in)  :: nj
        integer, intent (in)  :: nk
        integer, intent (in)  :: nmg

        ! Scalar settings
        integer, intent (in)  :: ischeme
        real, intent (in)  :: fmgrid
        real, intent (in)  :: fdamp

        ! End of argument declarations
        ! Begin working variables

        ! Net fluxes for each cell
        real, intent (inout) :: fsum(ni-1, nj-1, nk-1, 5)


        ! End of working variable declarations

        !! Evaluate source term at nodes, average to cell center
        !rho = cons(:, :, :, 1)
        !Vt = Vxrt(:, :, :, 3)
        !S = (rho*Vt*Vt + (P-Pref))/r
        !call node_to_cell(S, Sc, ni, nj, nk, 1)
        !Sc = Sc * vol(:,:,:,1)

        !! Sum fluxes to get the net flux into each cell
        !call sum_fluxes( &
        !    fluxi, fluxj, fluxk, &  ! Fluxes on the faces
        !    dAi, dAj, dAk, &        ! Cell geometry
        !    fsum, &                 ! Net flux
        !    ni, nj, nk, 5 &         ! Numbers of points for dummy args
        !)

         !Add on source term to the radial momentum eqn
        !fsum(:,:,:,3) = fsum(:,:,:,3)
        ! Add on body forces
        fsum = fsum + fb

        ! fsum now contains the sum of fluxes for all cells
        call multigrid_integrate(fsum, resid_cell(:,:,:,:,1), ijk_mg, dt_vol, fmgrid, ni-1, nj-1, nk-1, 5, nmg-1)

        ! Damp out the cell changes
        call damp(resid_cell(:,:,:,:,1), fdamp, ni-1, nj-1, nk-1)

        ! Time march and distribute to nodes
        call step(resid_cell, resid_node, ischeme, ni, nj, nk)

    end subroutine

    subroutine step(R, Rnode, ischeme, ni, nj, nk)

        real, intent (inout) :: R(ni-1, nj-1, nk-1, 5, 2)
        integer, intent (in) :: ischeme
        integer, intent (in)  :: ni
        integer, intent (in)  :: nj
        integer, intent (in)  :: nk

        real :: Rcell(ni-1, nj-1, nk-1, 5)
        real, intent (inout) :: Rnode(ni, nj, nk, 5)

        if (ischeme.eq.-1) then
            ! At the start, we have no previous time level available
            ! So just apply the one residual we have
            Rcell = R(:,:,:,:,1)
            ! Save the residual for next iteration
            R(:,:,:,:,2) = R(:,:,:,:,1)
        else if (ischeme.eq.0) then
        ! Otherwise, combine current and previous time level
        ! According to the selected time marching scheme
            Rcell = 2e0*R(:,:,:,:,1) - R(:,:,:,:,2)
            R(:,:,:,:,2) = R(:,:,:,:,1)
        else if (ischeme.eq.1) then
            Rcell = 2e0*R(:,:,:,:,1) - 1.65e0*R(:,:,:,:,2)
            R(:,:,:,:,2) = R(:,:,:,:,1) - 0.65e0*R(:,:,:,:,2)
        end if

        ! Distribute cell residual to nodes and add on
        call cell_to_node(Rcell, Rnode, ni, nj, nk, 5)

    end subroutine

    subroutine secondary(r, cons, Vxrt, u, ni, nj, nk)

        implicit none

        integer, intent (in)  :: ni
        integer, intent (in)  :: nj
        integer, intent (in)  :: nk

        real, intent (inout)  :: cons(ni, nj, nk, 5)
        real, intent (inout)  :: Vxrt(ni, nj, nk, 3)
        real :: halfVsq(ni, nj, nk)
        real, intent (inout)  :: u(ni, nj, nk)
        real, intent (inout)  :: r(ni, nj, nk)

        integer :: ic

        do ic = 1,3
            Vxrt(:,:,:, ic) = cons(:,:,:,ic+1)/cons(:,:,:,1)
        end do
        Vxrt(:,:,:,3) = Vxrt(:,:,:,3)/r
        halfVsq = 0.5e0*sum(Vxrt*Vxrt, 4)

        u = cons(:,:,:,5)/cons(:,:,:,1) - halfVsq

    end subroutine


    ! Apply negative feedback to damp down large changes, Denton (2017)
    subroutine damp(R, fdamp, ni, nj, nk)


        integer, intent (in) :: ni
        integer, intent (in) :: nj
        integer, intent (in) :: nk

        integer :: ip

        real, intent (inout) :: R(ni-1, nj-1, nk-1, 5)
        real, intent (in) :: fdamp
        real :: R_abs(ni-1, nj-1, nk-1, 5)
        real :: R_avg(5)

        ! Calculate absolute and average values over all cells
        R_abs = abs(R)
        R_avg = sum(sum(sum(R_abs,1),1),1)/real((ni-1)*(nj-1)*(nk-1))

        ! Apply damping to all cons Ruals
        R_avg = max(R_avg, 1e-9)
        do ip = 1, 5
            R(:,:,:,ip) = R(:,:,:,ip) &
                / (1e0 + R_abs(:,:,:,ip)/R_avg(ip)/fdamp)
        end do

    end subroutine

end module ember
